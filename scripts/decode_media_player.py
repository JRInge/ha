from argparse import ArgumentParser, Namespace


def get_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description=("Decode Home Assistant media_player supported_features"))

    parser.add_argument(
        'code',
        help=("Supported_features code to decipher."))
    return parser.parse_args()


features = {
            1: "Pause",
            2: "Seek",
            4: "Volume Set",
            8: "Volume Mute",
            16: "Previous Track",
            32: "Next Track",
            128: "Turn On",
            256: "Turn Off",
            512: "Play Media",
            1024: "Volume Step",
            2048: "Select Source",
            4096: "Stop",
            8192: "Clear Playlist",
            16384: "Play",
            32768: "Shuffle Set",
            65536: "Select Sound Mode",
            131072: "Browse Media",
            262144: "Repeat Set",
            524288: "Grouping",
           }
is_supported = {True: "[Supported]:   ", False: "[Unsupported]: "}

if __name__ == '__main__':
    args = get_args()

    for key, feature in features.items():
        print(f"{is_supported[bool(args.code & key)]}{features[key]}")
