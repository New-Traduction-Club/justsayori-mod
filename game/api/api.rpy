define CURRENT_VERSION = "1.0.0"

### load json
init python:
    import requests

    def version_tuple(v):
        return tuple(map(int, (v.split("."))))

    def show_ps_overlay():
        try:
            r = requests.get("https://traduction-club.live/api/justsayori/justsayori.json", timeout=5)
            data = r.json()
            latest_version = data.get("latest_version", "0.0.0")
            news = data.get("news", [])

            update_available = version_tuple(latest_version) > version_tuple(CURRENT_VERSION)
            if update_available:
                update_msg = "New Update available! ({})".format(latest_version)
            else:
                update_msg = "You have the latest version ({})".format(CURRENT_VERSION)

            renpy.show_screen("ps_overlay", update_msg=update_msg, news=news)
        except Exception as e:
            renpy.show_screen("ps_overlay", update_msg="Failed to load web features.", news=[])
