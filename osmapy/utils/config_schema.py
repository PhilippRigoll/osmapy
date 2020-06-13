schema = {
    'osm_api_url': {
        'required': True,
        'type': 'string'
    },
    'user_agent': {
        'required': True,
        'type': 'string'
    },
    'window_size': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'integer'
        }
    },
    'start_latitude': {
        'required': True,
        'type': 'float'
    },
    'start_longitude': {
        'required': True,
        'type': 'float'
    },
    'start_zoom': {
        'required': True,
        'type': 'integer'
    },
    'login_name': {
        'required': True,
        'type': 'string'
    },
    'password': {
        'required': True,
        'type': 'string',
        'nullable': True
    },

    'slippy_tiles': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'required': True,
                    'type': 'string',
                },
                'enabled': {
                    'required': True,
                    'type': 'boolean',
                },
                'urls': {
                    'required': True,
                    'type': 'list',
                    'schema': {
                        'type': 'string'
                    }
                }
            }

        }
    }
}
