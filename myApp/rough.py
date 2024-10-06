import geocoder

def get_current_location():
    # Get the current location based on IP address
    g = geocoder.ip('me')

    if g.ok:
        return g.address
    else:
        return "Location not available"

# Example usage
current_location = get_current_location()
print("Current Location:", current_location)
