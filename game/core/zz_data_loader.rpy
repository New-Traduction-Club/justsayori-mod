init 5 python:
    import store.fae_outfits as fae_outfits
    import store.fae_utilities as fae_utilities
    
    # NOTE: Custom outfits and persistent data are now loaded automatically by the OutfitManager.
    fae_utilities.log("Custom outfits loaded.")

    store.Sayori.load_persistent_outfit()

    if not store.Sayori._outfit:
        store.Sayori.setOutfit(fae_outfits.get_outfit("fae_uniform"))
    else:
        fae_utilities.log("--- OUTFIT LOAD SUCCESS: Sayori is wearing '{}' ---".format(store.Sayori._outfit.reference_name))
    