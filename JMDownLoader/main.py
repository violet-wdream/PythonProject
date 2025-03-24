
import argparse
import jmcomic


def main():
    parser = argparse.ArgumentParser(description='Download album using jmcomic.')
    parser.add_argument('--album_id', default=422866, type=str, help='The ID of the album to download')
    args = parser.parse_args()

    option = jmcomic.create_option_by_file('option.yml')
    jmcomic.download_album(args.album_id, option)  # 传入要下载的album的id，即可下载整个album到本地.


if __name__ == '__main__':
    main()