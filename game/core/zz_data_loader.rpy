init 5 python:
    import store.fae_outfits as fae_outfits
    import store.fae_utilities as fae_utilities
    
    fae_outfits.load_custom_wearables()
    fae_outfits.FAEWearable.load_all()
    fae_outfits.load_custom_outfits()
    fae_outfits.FAEOutfit.load_all()
    fae_utilities.log("Custom outfits loaded.")

    store.Sayori.load_persistent_outfit()

    if not store.Sayori._outfit:
        store.Sayori.setOutfit(fae_outfits.get_outfit("fae_uniform"))
    else:
        fae_utilities.log("--- OUTFIT LOAD SUCCESS: Sayori is wearing '{}' ---".format(store.Sayori._outfit.reference_name))
    