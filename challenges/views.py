from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Challenge, Report, HiddenChallenge
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, Http404
from io import BytesIO
import os

def extract_gps_from_image(image_file):
    """
    Extract GPS coordinates from image file (supports JPEG, PNG, HEIC).
    Returns (latitude, longitude) tuple or (None, None) if not found.
    """
    file_ext = os.path.splitext(image_file.name)[1].lower()
    is_heic = file_ext == '.heic'
    
    try:
        # Try using Pillow (PIL) - most common library
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            # For HEIC files, try to register pillow-heif support
            if is_heic:
                try:
                    from pillow_heif import register_heif_opener
                    register_heif_opener()
                except ImportError:
                    # pillow-heif not installed, will try exifread instead
                    pass
            
            image_file.seek(0)
            image_bytes = image_file.read()
            image = Image.open(BytesIO(image_bytes))
            
            # Get EXIF data
            exif_data = image.getexif()
            if not exif_data:
                return None, None
            
            # Find GPS info tag
            gps_info = None
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    gps_info = value
                    break
            
            if not gps_info:
                return None, None
            
            # Extract GPS coordinates
            gps_data = {}
            for tag_id, value in gps_info.items():
                tag = GPSTAGS.get(tag_id, tag_id)
                gps_data[tag] = value
            
            # Get latitude and longitude
            lat = gps_data.get('GPSLatitude')
            lat_ref = gps_data.get('GPSLatitudeRef', 'N')
            lon = gps_data.get('GPSLongitude')
            lon_ref = gps_data.get('GPSLongitudeRef', 'E')
            
            if lat and lon:
                # Convert from degrees, minutes, seconds to decimal
                def dms_to_dd(dms, ref):
                    degrees = float(dms[0])
                    minutes = float(dms[1])
                    seconds = float(dms[2])
                    dd = degrees + minutes / 60.0 + seconds / 3600.0
                    if ref in ['S', 'W']:
                        dd = -dd
                    return dd
                
                latitude = dms_to_dd(lat, lat_ref)
                longitude = dms_to_dd(lon, lon_ref)
                return latitude, longitude
                    
        except ImportError:
            # Pillow not available, try exifread
            pass
        
        # Try exifread as fallback (works better with HEIC sometimes)
        try:
            import exifread
            # Reset file pointer
            image_file.seek(0)
            tags = exifread.process_file(BytesIO(image_file.read()), details=False)
            
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = tags['GPS GPSLatitude']
                lat_ref_tag = tags.get('GPS GPSLatitudeRef')
                lon = tags['GPS GPSLongitude']
                lon_ref_tag = tags.get('GPS GPSLongitudeRef')
                
                # Get reference direction
                lat_ref = str(lat_ref_tag.values[0]) if lat_ref_tag else 'N'
                lon_ref = str(lon_ref_tag.values[0]) if lon_ref_tag else 'E'
                
                def dms_to_dd(dms, ref):
                    # exifread returns values as tuples of (numerator, denominator)
                    lat_deg = float(dms.values[0][0]) / float(dms.values[0][1])
                    lat_min = float(dms.values[1][0]) / float(dms.values[1][1])
                    lat_sec = float(dms.values[2][0]) / float(dms.values[2][1])
                    dd = lat_deg + lat_min / 60.0 + lat_sec / 3600.0
                    if ref in ['S', 'W']:
                        dd = -dd
                    return dd
                
                latitude = dms_to_dd(lat, lat_ref)
                longitude = dms_to_dd(lon, lon_ref)
                return latitude, longitude
        except (ImportError, AttributeError, IndexError, KeyError, TypeError):
            # exifread not available or couldn't parse - that's okay, client-side will handle it
            pass
                
    except Exception as e:
        # Log error but don't fail - this is just a fallback
        # Client-side extraction should handle HEIC files
        # Suppress expected errors for HEIC files without pillow-heif
        if is_heic and "cannot identify image file" in str(e):
            # This is expected for HEIC files without pillow-heif - client-side will handle it
            pass
        else:
            # Log unexpected errors (but don't fail)
            pass
    
    return None, None

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.heic']

@login_required
def upload_image(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        lat_str = request.POST.get("latitude")
        lon_str = request.POST.get("longitude")
        
        if not image:
            return render(request, "challenges/upload.html", {
                "error": "Please upload an image.",
                "mapbox_token": settings.MAPBOX_TOKEN
            })
            
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return render(request, "challenges/upload.html", {
                "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
                "mapbox_token": settings.MAPBOX_TOKEN
            })
        
        # If coordinates not provided, try to extract from image EXIF data
        # Note: For HEIC files, client-side extraction (ExifReader) should work better
        if not lat_str or not lon_str:
            # Save file position before reading
            image.seek(0)
            extracted_lat, extracted_lon = extract_gps_from_image(image)
            # Reset file pointer after reading (needed for Django to save the file)
            image.seek(0)
            if extracted_lat and extracted_lon:
                lat_str = str(extracted_lat)
                lon_str = str(extracted_lon)
            else:
                # For HEIC files, suggest using client-side extraction
                heic_hint = ""
                if ext == '.heic':
                    heic_hint = " For HEIC files, make sure to allow the page to read GPS data from your image when prompted."
                return render(request, "challenges/upload.html", {
                    "error": f"Please drop a pin on the map. (No GPS data found in image via server-side extraction){heic_hint}",
                    "mapbox_token": settings.MAPBOX_TOKEN
                })
        
        lat, lon = float(lat_str), float(lon_str)
        
        # Convert HEIC files to JPEG for browser compatibility
        if ext == '.heic':
            try:
                from PIL import Image
                # Try to register HEIC support
                try:
                    from pillow_heif import register_heif_opener
                    register_heif_opener()
                except ImportError:
                    # pillow-heif not installed - HEIC conversion won't work
                    return render(request, "challenges/upload.html", {
                        "error": "HEIC files require pillow-heif to be installed. Please install it with: pip install pillow-heif, or convert your image to JPEG/PNG before uploading.",
                        "mapbox_token": settings.MAPBOX_TOKEN
                    })
                
                # Read the HEIC file
                image.seek(0)
                img = Image.open(image)
                
                # Convert to RGB (HEIC might be in other color modes)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPEG in memory
                output = BytesIO()
                img.save(output, format='JPEG', quality=95)
                output.seek(0)
                
                # Create a new InMemoryUploadedFile with JPEG extension
                image_name = os.path.splitext(image.name)[0] + '.jpg'
                image = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    image_name,
                    'image/jpeg',
                    output.tell(),
                    None
                )
            except Exception as e:
                # If conversion fails, show error to user
                return render(request, "challenges/upload.html", {
                    "error": f"Could not convert HEIC file to JPEG: {str(e)}. Please try converting the image to JPEG/PNG before uploading.",
                    "mapbox_token": settings.MAPBOX_TOKEN
                })
        
        Challenge.objects.create(
            uploader=request.user,
            image=image,
            latitude=float(lat),
            longitude=float(lon),
        )
        return redirect("home.index")

    # GET request, load map
    return render(request, "challenges/upload.html", {
        "mapbox_token": settings.MAPBOX_TOKEN
    })


def serve_converted_image(request, challenge_id):
    """
    Serve a converted JPEG version of a HEIC image if needed.
    This handles existing HEIC files that weren't converted on upload.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    if not challenge.image:
        raise Http404("Image not found")
    
    try:
        image_path = challenge.image.path
    except ValueError:
        # Image might not exist on filesystem
        raise Http404("Image file not found")
    
    if not os.path.exists(image_path):
        raise Http404("Image file not found on disk")
    
    image_ext = os.path.splitext(image_path)[1].lower()
    
    # If it's already a JPEG/PNG, redirect to the direct URL
    if image_ext in ['.jpg', '.jpeg', '.png']:
        from django.shortcuts import redirect
        return redirect(challenge.image.url)
    
    # If it's HEIC, try to convert it
    if image_ext == '.heic':
        try:
            from PIL import Image
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            except ImportError:
                # If pillow-heif not available, try to serve original (won't work in browser but at least won't crash)
                from django.views.static import serve
                return serve(request, challenge.image.name, document_root=settings.MEDIA_ROOT)
            
            # Open and convert the HEIC image
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # Return as HTTP response
            response = HttpResponse(output.read(), content_type='image/jpeg')
            response['Content-Disposition'] = f'inline; filename="{os.path.splitext(os.path.basename(challenge.image.name))[0]}.jpg"'
            return response
        except Exception as e:
            # If conversion fails, try to serve original (won't work but won't crash)
            from django.views.static import serve
            return serve(request, challenge.image.name, document_root=settings.MEDIA_ROOT)
    
    # For other formats, try to serve directly
    from django.views.static import serve
    return serve(request, challenge.image.name, document_root=settings.MEDIA_ROOT)


@login_required
def report_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method != "POST":
        return redirect(reverse('gameplay.play', args=[challenge.id]))

    reason = request.POST.get('reason')
    details = request.POST.get('details', '').strip()

    if not reason:
        return redirect(f"{reverse('gameplay.play', args=[challenge.id])}?reported=0")

    Report.objects.create(
        reporter=request.user,
        challenge=challenge,
        reason=reason,
        details=details,
    )

    HiddenChallenge.objects.get_or_create(user=request.user, challenge=challenge)

    return render(request, "gameplay/removed.html", {
        "message": "This photo has been removed from your play queue. Thank you for your help.",
        "next_url": reverse('gameplay.start'),
        "challenge": challenge,
    })

@user_passes_test(lambda u: u.is_superuser)
def review_reports(request):
    reports = Report.objects.all().order_by('-created_at')
    if request.method == "POST":
        action = request.POST.get("action")
        report_id = request.POST.get("report_id")
        report = get_object_or_404(Report, id=report_id)

        if action == "dismiss":
            HiddenChallenge.objects.filter(user=report.reporter, challenge=report.challenge).delete()
            report.delete()
        elif action == "remove":
            challenge = report.challenge
            challenge.is_active = False
            challenge.save()
            Report.objects.filter(challenge=challenge).delete()

        return redirect('challenges.review_reports')

    return render(request, "challenges/review_reports.html", {
        "reports": reports
    })
