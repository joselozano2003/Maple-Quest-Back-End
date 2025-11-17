from django.core.management.base import BaseCommand
from core.models import Location
import uuid
import os


class Command(BaseCommand):
    help = 'Seed the database with landmark locations from iOS app data'

    def handle(self, *args, **options):
        # Determine base URL based on environment
        endpoint_url = os.getenv('AWS_S3_ENDPOINT_URL')
        bucket_name = os.getenv('S3_BUCKET_NAME', 'maple-quest-images')
        
        if endpoint_url:
            # Local development with MinIO
            base_url = f"{endpoint_url}/{bucket_name}/locations"
        else:
            # Production with AWS S3
            region = os.getenv('AWS_REGION', 'us-west-2')
            base_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/locations"
        
        landmarks_data = [
            {
                "name": "Niagara Falls",
                "province": "Ontario",
                "description": "Niagara Falls is a breathtaking natural wonder on the border of Canada and the United States, known for its massive, powerful waterfalls and misty beauty. It's a popular destination for sightseeing, boat tours, and stunning views, especially from the Canadian side.",
                "latitude": "43.0946853",
                "longitude": "-79.039969",
                "points": 100,
                "default_image_url": f"{base_url}/niagara-falls.jpg"
            },
            {
                "name": "Hopewell Rocks Provincial Park",
                "province": "New Brunswick", 
                "description": "Hopewell Rocks Provincial Park in New Brunswick is famous for its towering flowerpot-shaped rock formations carved by the tides of the Bay of Fundy. Visitors can walk on the ocean floor at low tide and kayak among the rocks at high tide for a truly unique experience.",
                "latitude": "45.817655",
                "longitude": "-64.578458",
                "points": 80,
                "default_image_url": f"{base_url}/hopewell-rocks.jpg"
            },
            {
                "name": "Banff National Park",
                "province": "Alberta",
                "description": "Banff National Park, located in the Canadian Rockies, is renowned for its stunning turquoise lakes, majestic mountains, and abundant wildlife. It's a year-round destination for hiking, skiing, and exploring some of Canada's most breathtaking natural scenery.",
                "latitude": "51.497408",
                "longitude": "-115.926168",
                "points": 120,
                "default_image_url": f"{base_url}/banff.jpg"
            },
            {
                "name": "University of Calgary",
                "province": "Alberta",
                "description": "The University of Calgary is a leading Canadian research university known for its innovative programs, vibrant campus life, and strong ties to industry. Located in Alberta's largest city, it offers world-class education and opportunities in a dynamic, forward-thinking environment.",
                "latitude": "51.07848848773985",
                "longitude": "-114.13352874347278",
                "points": 50,
                "default_image_url": f"{base_url}/ucalgary.jpg"
            },
            {
                "name": "CN Tower",
                "province": "Ontario",
                "description": "One of the tallest freestanding structures in the world, offering panoramic city and lake views. It's famous for its glass floor and EdgeWalk experience.",
                "latitude": "43.64272921522629",
                "longitude": "-79.38712117632794",
                "points": 90,
                "default_image_url": f"{base_url}/cn-tower.jpg"
            },
            {
                "name": "Parliament Hill",
                "province": "Ontario",
                "description": "The heart of Canada's federal government. Its Gothic Revival architecture, daily ceremonies, and riverfront location make it an iconic national symbol.",
                "latitude": "45.42375180363914",
                "longitude": "-75.70093973205235",
                "points": 75,
                "default_image_url": f"{base_url}/parliament-hill.jpg"
            },
            {
                "name": "Capilano Suspension Bridge",
                "province": "British Columbia",
                "description": "A 137-metre-long swaying bridge over a forested canyon in North Vancouver. The park features treetop walkways, cliffside paths, and Indigenous cultural exhibits.",
                "latitude": "49.343021644932385",
                "longitude": "-123.1149244029921",
                "points": 85,
                "default_image_url": f"{base_url}/capilano-bridge.jpg"
            },
            {
                "name": "Château Frontenac",
                "province": "Québec",
                "description": "Historic grand hotel overlooking Old Québec, known for its castle-like architecture and river views.",
                "latitude": "46.81231686579934",
                "longitude": "-71.20521303872079",
                "points": 70,
                "default_image_url": f"{base_url}/chateau-frontenac.jpg"
            },
            {
                "name": "Peggy's Cove Lighthouse",
                "province": "Nova Scotia",
                "description": "Classic red lighthouse perched on rocky shores, surrounded by waves and picturesque fishing village scenery.",
                "latitude": "44.491936206399686",
                "longitude": "-63.91859253025372",
                "points": 65,
                "default_image_url": f"{base_url}/peggys-cove.jpg"
            }
        ]

        created_count = 0
        updated_count = 0

        for landmark in landmarks_data:
            # Generate unique location_id
            location_id = str(uuid.uuid4())[:10]
            while Location.objects.filter(location_id=location_id).exists():
                location_id = str(uuid.uuid4())[:10]

            # Check if location already exists by name
            existing_location = Location.objects.filter(name=landmark['name']).first()
            
            if existing_location:
                # Update existing location
                existing_location.description = landmark['description']
                existing_location.latitude = landmark['latitude']
                existing_location.longitude = landmark['longitude']
                existing_location.points = landmark['points']
                existing_location.default_image_url = landmark['default_image_url']
                existing_location.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated location: {landmark["name"]}')
                )
            else:
                # Create new location
                Location.objects.create(
                    location_id=location_id,
                    name=landmark['name'],
                    latitude=landmark['latitude'],
                    longitude=landmark['longitude'],
                    description=landmark['description'],
                    points=landmark['points'],
                    default_image_url=landmark['default_image_url']
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created location: {landmark["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding completed! Created: {created_count}, Updated: {updated_count}'
            )
        )