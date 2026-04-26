# resource_allocation.py
RESOURCE_CONFIG = {
    'database': {
        'postgresql': {'memory': '8GB', 'cpu': 4},
        'redis': {'memory': '4GB', 'cpu': 2},
        'influxdb': {'memory': '4GB', 'cpu': 2}
    },
    'workers': {
        'detection': {'count': 10, 'memory': '2GB', 'cpu': 1},
        'ml': {'count': 4, 'memory': '4GB', 'cpu': 2, 'gpu': True},
        'correlation': {'count': 5, 'memory': '2GB', 'cpu': 1}
    },
    'queues': {
        'kafka': {'memory': '8GB', 'cpu': 2},
        'rabbitmq': {'memory': '4GB', 'cpu': 1}
    }
}