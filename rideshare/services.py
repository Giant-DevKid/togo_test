import os
import requests
from geopy.distance import geodesic

from rideshare.models import (
    Vehicle, RideBooking, DriverRoute, RideBookingResponse
)

from whatsapp.services import (
    send_whatsapp_buttons,
    send_interactive_buttons_message,
    send_whatsapp_message
)

from conversation.services.message_service import (
    send_text,
)

THRESHOLD_KM = 15
ORS_API_KEY = os.getenv("ORS_API_KEY")

def get_user_vehicle(user):

    return Vehicle.objects.filter(
        user=user
    ).first()


def get_driver_routes(user):

    return DriverRoute.objects.filter(
        driver=user
    )




def calculate_price(distance_meters):

    distance_km = distance_meters / 1000

    base_fare = 1000

    per_km_rate = 250

    total = base_fare + (
        distance_km * per_km_rate
    )

    return round(total, 2)



def geocode_location(location_name):

    url = (
        "https://nominatim.openstreetmap.org/search"
    )

    params = {
        "q": f"{location_name}, Nigeria",
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "rideshare-app"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15,
    )

    data = response.json()

    if not data:

        return None

    location = data[0]

    return {
        "lat": float(location["lat"]),
        "lng": float(location["lon"]),
        "display_name": (
            location.get("display_name")
        )
    }



def get_route(start_lng, start_lat, end_lng, end_lat):

    url = 'https://api.openrouteservice.org/v2/directions/driving-car'

    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    body = {
        'coordinates': [
            [start_lng, start_lat],
            [end_lng, end_lat]
        ]
    }

    response = requests.post(
        url,
        json=body,
        headers=headers
    )

    data = response.json()

    route = data['routes'][0]

    return {
        'distance': route['summary']['distance'],
        'duration': route['summary']['duration'],
        'geometry': route['geometry']
    }



def get_route_data(
    start_lng,
    start_lat,
    end_lng,
    end_lat
):

    url = (
        "https://api.openrouteservice.org/"
        "v2/directions/driving-car/geojson"
    )

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "coordinates": [

            [start_lng, start_lat],

            [end_lng, end_lat]
        ]
    }

    response = requests.post(
        url,
        json=body,
        headers=headers
    )

    data = response.json()

    feature = data["features"][0]

    properties = feature["properties"]

    geometry = feature["geometry"]

    return {

        "distance": (
            properties["summary"]["distance"]
        ),

        "duration": (
            properties["summary"]["duration"]
        ),

        "geometry": geometry,

        "coordinates": (
            geometry["coordinates"]
        ),

        "encoded_polyline": (
            str(geometry)
        ),
    }



def update_driver_route(
    driver,
    route_id,
    start_name=None,
    end_name=None
):

    route = (
        DriverRoute.objects
        .filter(
            id=route_id,
            driver=driver
        )
        .first()
    )


    if not route:

        return None

    updated_start_name = (
        start_name
        or route.start_name
    )

    updated_end_name = (
        end_name
        or route.end_name
    )

    start = geocode_location(
        updated_start_name
    )

    end = geocode_location(
        updated_end_name
    )


    if not start or not end:

        return None

    route_data = get_route_data(

        start["lng"],
        start["lat"],

        end["lng"],
        end["lat"],
    )


    route.start_name = (
        updated_start_name
    )

    route.end_name = (
        updated_end_name
    )

    route.start_lat = start["lat"]
    route.start_lng = start["lng"]

    route.end_lat = end["lat"]
    route.end_lng = end["lng"]

    route.distance_meters = (
        route_data["distance"]
    )

    route.duration_seconds = (
        route_data["duration"]
    )

    route.route_geometry = (
        route_data["geometry"]
    )

    route.encoded_polyline = (
        route_data["geometry"]
    )

    route.save()

    return route



def is_near_route(
    point,
    route_points
):

    for route_point in route_points:

        distance = geodesic(
            point,
            (
                route_point[1],
                route_point[0]
            )
        ).km

        if distance <= THRESHOLD_KM:

            return True

    return False



def create_driver_route(
    driver,
    start_name,
    end_name
):

    start = geocode_location(
        start_name
    )

    end = geocode_location(
        end_name
    )

    route_data = get_route_data(

        start["lng"],
        start["lat"],

        end["lng"],
        end["lat"],
    )

    route = DriverRoute.objects.create(

        driver=driver,

        start_name=start_name,

        end_name=end_name,

        start_lat=start["lat"],
        start_lng=start["lng"],

        end_lat=end["lat"],
        end_lng=end["lng"],

        distance_meters=(
            route_data["distance"]
        ),

        duration_seconds=(
            route_data["duration"]
        ),

        route_geometry=(
            route_data["geometry"]
        ),

        encoded_polyline=(
            route_data["geometry"]
        ),

        is_active=True,
    )

    return route



def find_matching_routes(
    pickup_point,
    destination_point
):

    matches = []

    routes = DriverRoute.objects.filter(
        is_active=True
    )

    for route in routes:

        points = (
            route.route_geometry[
                "coordinates"
            ]
        )

        pickup_match = is_near_route(
            pickup_point,
            points
        )

        destination_match = is_near_route(
            destination_point,
            points
        )

        if pickup_match and destination_match:

            matches.append(route)

    return matches



def create_booking(
    passenger,
    pickup_name,
    destination_name,
    pickup,
    destination,
    route_data
):

    estimated_price = calculate_price(
        route_data["distance"]
    )

    booking = RideBooking.objects.create(

        passenger=passenger,

        pickup_name=pickup_name,

        destination_name=destination_name,

        pickup_lat=pickup["lat"],

        pickup_lng=pickup["lng"],

        destination_lat=destination["lat"],

        destination_lng=destination["lng"],

        estimated_price=estimated_price,

        distance_meters=route_data["distance"],

        route_geometry=route_data[
            "geometry"
        ],

        encoded_polyline=route_data[
            "geometry"
        ],
    )

    return booking



def notify_matching_riders(
    booking,
    matched_routes
):

    for route in matched_routes:

        rider = route.driver

        buttons = [

            {
                "id":
                    f"accept_booking_{booking.id}",

                "title":
                    "Accept",
            },

            {
                "id":
                    f"reject_booking_{booking.id}",

                "title":
                    "Reject",
            },

            {
                "id":
                    f"change_price_{booking.id}",

                "title":
                    "Change Price",
            },
        ]

        send_interactive_buttons_message(

            to=rider.phone_no,

            body=(

                "New Ride Booking 🚗\n\n"

                f"Pickup: "
                f"{booking.pickup_name}\n"

                f"Destination: "
                f"{booking.destination_name}\n\n"

                f"Estimated Price: "
                f"₦{booking.estimated_price}"
            ),

            buttons=buttons,
        )



def notify_passenger_of_booking_update(
    booking
):

    responses = RideBookingResponse.objects.filter(
        booking=booking,
        response__in=[
            "ACCEPTED",
            "PRICE_UPDATED"
        ]
    )

    if not responses.exists():
        return

    buttons = []

    body = (
        "Riders Available 🚗\n\n"
    )

    counter = 1

    for response in responses:

        rider = response.rider

        vehicle = getattr(
            rider,
            "vehicles",
            None
        )

        body += (

            f"{counter}. "
            f"{rider.first_name}\n"

            f"Vehicle: "
            f"{vehicle.brand if vehicle else 'N/A'}\n"

            f"Plate: "
            f"{vehicle.plate_no if vehicle else 'N/A'}\n"

            f"Price: "
            f"₦{response.updated_price}\n\n"
        )

        buttons.append({

            "id":
                f"select_rider_{response.id}",

            "title":
                str(counter),
        })

        counter += 1

    send_interactive_buttons_message(

        to=booking.passenger.phone_no,

        body=body,

        buttons=buttons,
    )



def delete_driver_route(
    driver,
    route_id
):

    route = (
        DriverRoute.objects
        .filter(
            id=route_id,
            driver=driver
        )
        .first()
    )

    if not route:

        return None

    route.delete()

    return route


def notify_riders(
    booking,
    matched_routes
):

    for route in matched_routes:

        rider = route.driver

        # =================================
        # CREATE RESPONSE ENTRY
        # =================================

        response = (
            RideBookingResponse.objects
            .create(

                booking=booking,

                rider=rider,

                route=route,

                response="PENDING"
            )
        )

        # =================================
        # SEND AI MESSAGE
        # =================================

        send_text(

            rider.phone_no,

            (
                "🚘 New Ride Request\n\n"

                f"Request ID: "
                f"{response.id}\n\n"

                f"Pickup: "
                f"{booking.pickup_name}\n"

                f"Destination: "
                f"{booking.destination_name}\n"

                f"Estimated Price: "
                f"₦{booking.estimated_price}\n\n"

                "You can reply:\n\n"

                f"• accept {response.id}\n"

                f"• reject {response.id}\n"

                f"• offer {response.id} 4500"
            )
        )

