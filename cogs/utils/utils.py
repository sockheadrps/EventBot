import datetime

def create_event(Event):
    new_event = Event()
    new_event.user= "sockheadrps"
    new_event.title = "my super cool event"
    new_event.game_type = "Custom ARAMS"
    
    current_time = datetime.datetime.now()
    new_time = current_time + datetime.timedelta(minutes=5)
    print(f"time set for {new_time}")
    new_event.time = new_time.strftime("%I:%M%p")
    new_event.time_zone = "-5"
    new_event.banner = "https://cdn.discordapp.com/attachments/712798473409396748/1190474253506727936/image.png?ex=65a1ee8b&is=658f798b&hm=f173594597e6d986f70b96149e4d1abe4985ecc3b87f9fc109a299c018481dfa&"



    return new_event
