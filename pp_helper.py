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


def num100_from_accuracy(accuracy, total_hit):
    '''
    num300 + num100 = total_hit
    (num100 * 100 + num300 * 300) / (total_hit * 300) = accuracy
    => 
        num300 = total_hit - num100
        num100 = 3 * accuracy * total_hit - 3 * num300
    =>
        num100 =  (3 * accuracy * total_hit) -3 * total_hit + 3 * num100 
        -2 * num100 = (3 * accuracy * total_hit) -3 * total_hit
        num100 = ((3 * accuracy * total_hit) - (3 * total_hit)) / -2
    '''
    return ((3 * accuracy * total_hit) - (3 * total_hit)) / -2.0


def compute_pp(beatmap, attributes, accuracy=1):
    # TODO: check if valid beatmap to calculate pp
    aim_val = compute_aim_value(beatmap, attributes, accuracy)
    speed_val = compute_speed_value(beatmap, attributes, accuracy)
    accuracy_value = compute_accuracy_value(beatmap, attributes, accuracy)
    flashlight_value = compute_flashlight_value(beatmap, attributes, accuracy)

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


def compute_aim_value(beatmap, attributes, accuracy):
    '''
    Notice that:
        Effective miss count is always 0.
        Combo scaling factor is always 1.
        Slider neft factor is always 1.
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

    aim_val *= accuracy
    aim_val *= 0.98 + (pow(attributes['overall_difficulty'], 2) / 2500.0)

    return aim_val


def compute_speed_value(beatmap, attributes, accuracy):
    '''
    Notice that:
        Effective miss count is always 0.
        Combo scaling factor is always 1.
        Slider neft factor is always 1.
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

    num_total_hits = beatmap["hit_object_count"]
    num100 = num100_from_accuracy(accuracy, num_total_hits)
    num300 = num_total_hits - num100

    relevant_total_diff = num_total_hits - attributes['speed_note_count']
    relevant_count_great = max(0.0, num300 - relevant_total_diff)
    relevant_count_ok = max(0.0, num100 - max(0.0, relevant_total_diff - num300))

    relevant_accuracy = 0.0 if attributes['speed_note_count'] == 0.0 else (
        relevant_count_great * 6.0 + relevant_count_ok * 2.0) / (attributes['speed_note_count'] * 6.0)

    speed_val *= (0.95 + pow(attributes['overall_difficulty'], 2) / 750.0) * (
        pow((accuracy + relevant_accuracy) / 2, (14.5 - max(attributes['overall_difficulty'], 8)) / 2)
    )

    return speed_val


def compute_accuracy_value(beatmap, attributes, accuracy):
    '''
    Notice that:
        Better Accuarcy Percentage is always 1.
    '''
    num_hit_object_with_accuracy = beatmap['count_circles']
    num_total_hits = beatmap["hit_object_count"]
    num100 = num100_from_accuracy(accuracy, num_total_hits)
    num300 = num_total_hits - num100
    better_accuracy_percentage = 0 if num_hit_object_with_accuracy <= 0 else (
        ((num300 - (num_total_hits - num_hit_object_with_accuracy)) * 6 + num100 * 2) / (num_hit_object_with_accuracy * 6)
    )

    accuracy_val = pow(1.52163, attributes['overall_difficulty']) * pow(better_accuracy_percentage, 24) * 2.83
    accuracy_val *= min(1.15, pow(num_hit_object_with_accuracy / 1000.0, 0.3))

    # TODO: add bonus for hidden and flashlight
    return accuracy_val


def compute_flashlight_value(beatmap, attributes, accuracy):
    # TODO:
    return 0
