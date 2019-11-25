from . import models
import random
import string


def generate_identifier():
    def generate_random():
        ran_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        return ran_id
    ran_id = generate_random()
    print('ran id generated: {}'.format(ran_id))
    while models.HueAuth.objects.filter(identifier=ran_id).exists():
        ran_id = generate_random()
    return ran_id