


AspectBusiness = "Business Service"
AspectCheckin = "Check in"
AspectClean = "Cleanliness"
AspectLocation = "Location"
AspectOverall = "Overall"
AspectRoom = "Rooms"
AspectService = "Service"
AspectValue = "Value"
AspectSleep = "Sleep Quality"

def normalize_ratings(dest_ratings,dest_label,src_ratings,src_label):
    if src_label in src_ratings:
        dest_ratings[dest_label] = float(src_ratings[src_label])
