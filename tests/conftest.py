import pytest
from app import create_app

# Fixture "app_context" automatycznie uruchamia aplikację Flask
# przed każdym testem i zapewnia dostęp do `app.app_context()`
@pytest.fixture(autouse=True)
def app_context():
    # Tworzymy nową instancję aplikacji
    app = create_app()
    # Wchodzimy w kontekst aplikacji, by móc korzystać z rozszerzeń (np. db)
    with app.app_context():
        # `yield` pozwala testom wykonać kod w kontekście
        yield