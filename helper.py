import math
import os
import re

import httpx

base_url = "https://osu.ppy.sh/api/v2"


def parse_beatmapset_url(url):
    x = re.search("([0-9]+)#osu/([0-9]+)", url)
    beatmapset_id = x[1]
    beatmap_id = x[2]
    return (beatmapset_id, beatmap_id)


async def get_token():
    data = {
        "client_id": os.environ["OSU_OAUTH_CLIENT_ID"],
        "client_secret": os.environ["OSU_OAUTH_SECRET"],
        "grant_type": "client_credentials",
        "scope": "public"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post('https://osu.ppy.sh/oauth/token', json=data)
        return r.json()["access_token"]


async def get_beatmap_data(token, beatmap_id):
    headers = {'Authorization': f'Bearer {token}'}

    async with httpx.AsyncClient() as request:
        beatmap_coroutine = request.get(f'{base_url}/beatmaps/{beatmap_id}', headers=headers)
        attributes_coroutine = request.post(f'{base_url}/beatmaps/{beatmap_id}/attributes', headers=headers)

        beatmap = (await beatmap_coroutine).json()
        attributes = (await attributes_coroutine).json()['attributes']

    beatmap['hit_object_count'] = beatmap['count_circles'] + beatmap['count_sliders'] + beatmap['count_spinners']
    return (beatmap, attributes)


def compute_pp(beatmap, attributes):
    # TODO: check if valid beatmap to calculate pp
    aim_val = compute_aim_value(beatmap, attributes)
    speed_val = compute_speed_value(beatmap, attributes)
    accuracy_value = compute_accuracy_value(beatmap, attributes)
    flashlight_value = compute_flashlight_value(beatmap, attributes)

    # TODO: change multipler value for No fail and Spun out mods
    multiplier = 1.14
    pp = pow(
        pow(aim_val, 1.1) + pow(speed_val, 1.1) + pow(accuracy_value, 1.1) + pow(flashlight_value, 1.1),
        1.0 / 1.1
    ) * multiplier

    return round(pp, 2)


def compute_length_bonus(beatmap):
    hit_object_count = beatmap["hit_object_count"]
    long_map_bonus = math.log10(hit_object_count / 2000.0) * 0.5 if hit_object_count > 2000 else 0.0
    return 0.95 + 0.4 * min(1.0, hit_object_count / 2000.0) + long_map_bonus


def compute_aim_value(beatmap, attributes):
    '''
    Notice that:
        Effective miss count is always 0.
        Combo scaling factor is always 1.
        Slider neft factor is always 1.
        Accuracy is always 1.
    '''

    aim_val = 5.0 * max(1.0, attributes['aim_difficulty'] / 0.0675) - 4.0
    aim_val = pow(aim_val, 3.0) / 100000.0

    length_bonus = compute_length_bonus(beatmap)

    aim_val *= length_bonus

    approach_rate = attributes['approach_rate']
    approach_rate_factor = 0.0
    if approach_rate > 10.33:
        approach_rate_factor = 0.3 * (approach_rate - 10.33)
    elif approach_rate < 8.0:
        approach_rate_factor = 0.05 * (8.0 - approach_rate)

    aim_val *= 1.0 + approach_rate_factor * length_bonus

    # TODO: apply HD mod reward
    # if ((_mods & EMods::Hidden) > 0) _aimValue *= 1.0f + 0.04f * (12.0f - approachRate)

    aim_val *= 0.98 + (pow(attributes['overall_difficulty'], 2) / 2500.0)

    return aim_val


def compute_speed_value(beatmap, attributes):
    '''
    Notice that:
        Effective miss count is always 0.
        Combo scaling factor is always 1.
        Slider neft factor is always 1.
        Accuracy is always 1.
        Relevant accuracy is always 1
    '''

    speed_val = pow(5.0 * max(1.0, attributes['speed_difficulty'] / 0.0675) - 4.0, 3.0) / 100000.0

    length_bonus = compute_length_bonus(beatmap)
    speed_val *= length_bonus

    approach_rate = attributes['approach_rate']
    approach_rate_factor = 0.0
    if approach_rate > 10.33:
        approach_rate_factor = 0.3 * (approach_rate - 10.33)

    speed_val *= 1.0 + approach_rate_factor * length_bonus

    # TODO: apply HD mod reward
    # if ((_mods & EMods::Hidden) > 0) _aimValue *= 1.0f + 0.04f * (12.0f - approachRate)

    speed_val *= (0.95 + pow(attributes['overall_difficulty'], 2) / 750.0)
    return speed_val


def compute_accuracy_value(beatmap, attributes):
    '''
    Notice that:
        Better Accuarcy Percentage is always 1.
    '''
    hit_object_with_accuracy_count = beatmap['count_circles']

    accuracy_val = pow(1.52163, attributes['overall_difficulty']) * 2.83
    accuracy_val *= min(1.15, pow(hit_object_with_accuracy_count / 1000.0, 0.3))

    # TODO: add bonus for hidden and flashlight
    return accuracy_val


def compute_flashlight_value(beatmap, attributes):
    # TODO:
    return 0
