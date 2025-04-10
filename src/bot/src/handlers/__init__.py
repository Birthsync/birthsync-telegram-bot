from aiogram import Router


def get_handlers_router() -> Router:
    from src.handlers.user.categories import (
        show_categories_handler,
        add_category_callback_handler,
        show_category_card_callback_handler
    )
    from src.handlers.user.contacts import (
        show_contacts_handler,
        add_contact_callback_handler
    )
    from src.handlers.user.general import (
        start_handler,
        messages_handler,
        back_callback_handler,
        close_callback_handler
    )
    from src.handlers.user.general.deeplinks import (
        start_add_contacts_handler
    )
    from src.handlers.user.profile import (
        show_profile_handler,
    )
    from src.handlers.user.wishlists import (
        show_wishlists_handler,
        add_wishlist_callback_handler,
        ai_gifts_wishlist_callback_handler
    )

    main_router = Router(name='main')

    # Categories
    main_router.include_router(show_categories_handler.router)
    main_router.include_router(add_category_callback_handler.router)
    main_router.include_router(show_category_card_callback_handler.router)

    # Contacts
    main_router.include_router(show_contacts_handler.router)
    main_router.include_router(add_contact_callback_handler.router)

    # Profile
    main_router.include_router(show_profile_handler.router)

    # Wishlists
    main_router.include_router(show_wishlists_handler.router)
    main_router.include_router(add_wishlist_callback_handler.router)
    main_router.include_router(ai_gifts_wishlist_callback_handler.router)

    # General
    main_router.include_router(start_add_contacts_handler.router)
    main_router.include_router(back_callback_handler.router)
    main_router.include_router(close_callback_handler.router)
    main_router.include_router(start_handler.router)
    main_router.include_router(messages_handler.router)

    return main_router
