#import meli
#from ..python_sdk.meli.configuration
from ..sdk.meli.configuration import  Configuration
from ..sdk.meli.api_client import ApiClient
from ..sdk.meli.api.o_auth_2_0_api import OAuth20Api
from ..sdk.meli.exceptions import ApiException
API_URL  = 'https://api.mercadolibre.com'
AUTH_URL = 'https://auth.mercadopago.com.pe'
INFO_URL = 'https://api.mercadolibre.com/users/me'

COUNTRIES = [
    ('MLM', 'Mexico'),
    ('MLV', 'Venezuela'),
    ('MLB', 'Brasil'),
    ('MPE', 'Perú'),
    ('MCU', 'Cuba'),
    ('MNI', 'Nicaragua'),
    ('MRD', 'Dominicana'),
    ('MCO', 'Colombia'),
    ('MCR', 'Costa Rica'),
    ('MBO', 'Bolivia'),
    ('MHN', 'Honduras'),
    ('MLC', 'Chile'),
    ('MGT', 'Guatemala'),
    ('MEC', 'Ecuador'),
    ('MPY', 'Paraguay'),
    ('MPA', 'Panamá'),
    ('MSV', 'El Salvador'),
    ('MLA', 'Argentina'),
    ('MLU', 'Uruguay')]

CURRENCIES = [
    ('ARS', 'Peso argentino'),
    ('BOB', 'Boliviano'),
    ('BRL', 'Real'),
    ('CLF', 'Unidad de Fomento'),
    ('CLP', 'Peso Chileno'),
    ('COP', 'Peso colombiano'),
    ('CRC', 'Colones'),
    ('CUC', 'Peso Cubano Convertible'),
    ('CUP', 'Peso Cubano'),
    ('DOP', 'Peso Dominicano'),
    ('EUR', 'Euro'),
    ('GTQ', 'Quetzal Guatemalteco'),
    ('HNL', 'Lempira'),
    ('MXN', 'Peso Mexicano'),
    ('NIO', 'Córdoba'),
    ('PAB', 'Balboa'),
    ('PEN', 'Soles'),
    ('PYG', 'Guaraní'),
    ('USD', 'Dólar'),
    ('UYU', 'Peso Uruguayo'),
    ('VEF', 'Bolivar fuerte'),
    ('VES', 'Bolivar Soberano')]

CONDITIONS = [
    ("new", "Nuevo"),
    ("used", "Usado"),
    ("not_specified","No especificado")
]

def get_token(client_id, client_secret, redirect_uri, code, refresh_token):
    configuration2 = Configuration(
        host = API_URL
    )

    with ApiClient() as api_client:
        api_instance = OAuth20Api(api_client)
        grant_type = 'refresh_token'
    
        try:
            api_response = api_instance.get_token(grant_type=grant_type, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, code=code, refresh_token=refresh_token)
            return api_response
        except ApiException as err:
            return None


