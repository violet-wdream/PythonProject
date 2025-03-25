import argparse
import jmcomic
import requests
import subprocess
import os
import datetime
def push_to_github(album_id, album_name, repo_path=None):
    """
    将下载的文件推送到GitHub
    Args:
        album_id: 专辑ID
        album_name: 专辑名称
        repo_path: Git仓库路径，默认为当前目录
    Returns:
        bool: 是否成功推送
    """
    try:
        # 如果未指定仓库路径，使用当前目录
        if repo_path is None:
            repo_path = os.getcwd()
        
        # 切换到仓库目录
        os.chdir(repo_path)
        print(f"正在将专辑 {album_id}:{album_name} 推送到GitHub...")
        
        # 获取当前时间作为提交信息的一部分
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Add album {album_id}: {album_name} - {now}"
        
        # 执行Git命令
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print(f"专辑 {album_id}:{album_name} 已成功推送到GitHub")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {e}")
        print("请确保已配置好GitHub仓库并有适当的推送权限")
        return False
    
    except Exception as e:
        print(f"推送到GitHub时出错: {e}")
        return False
def get_total_size(album_id, option):
    """
    获取指定专辑的所有文件总大小（字节）
    Args:
        album_id: 专辑ID
        option: jmcomic选项对象
    
    Returns:
        int: 总字节数
    """
    total_size = 0
    total_files = 0
    headers = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'identity'  # 请求未压缩内容以获取真实大小
    }
    
    try:
        # 创建下载器但不实际下载
        with jmcomic.new_downloader(option) as dler:
            print(f"获取专辑{album_id}的信息...")
            # 获取专辑信息
            client = dler.client_for_album(album_id)
            album = client.get_album_detail(album_id)
            print(f"获取专辑{album_id}的章节，专辑名称: {album.name}")
            
            # 遍历所有章节
            for photo_idx, photo in enumerate(album):
                # 确保photo包含图片URL等必要信息
                client.check_photo(photo)
                print(f"获取章节[{photo_idx+1}/{len(album)}] {photo.name}的图片...")
                
                # 遍历章节中的所有图片
                for img_idx, image in enumerate(photo):
                    print(f"处理图片[{img_idx+1}/{len(photo)}]: {image.download_url}")
                    total_files += 1
                    
                    try:
                        # 方法1: 尝试HEAD请求并指定Accept-Encoding: identity
                        head_resp = requests.head(image.download_url, timeout=10, headers=headers)
                        
                        if head_resp.status_code == 200 and 'content-length' in head_resp.headers:
                            size = int(head_resp.headers['content-length'])
                            total_size += size
                            print(f"图片大小: {size} 字节")
                        else:
                            # 方法2: 如果HEAD请求未返回大小，使用GET请求部分内容
                            range_headers = headers.copy()
                            range_headers['Range'] = 'bytes=0-0'
                            head_resp = requests.get(image.download_url, timeout=10, headers=range_headers)
                            
                            if 'content-range' in head_resp.headers:
                                content_range = head_resp.headers['content-range']
                                total_bytes = int(content_range.split('/')[1])
                                total_size += total_bytes
                                print(f"图片大小(通过Content-Range): {total_bytes} 字节")
                            else:
                                # 方法3: 下载完整内容并获取大小
                                print("无法通过HEAD或Range请求获取大小，将下载完整内容...")
                                get_resp = requests.get(image.download_url, timeout=15, headers=headers)
                                if get_resp.status_code == 200:
                                    size = len(get_resp.content)
                                    total_size += size
                                    print(f"图片大小(通过下载): {size} 字节")
                                else:
                                    print(f"警告: 无法获取图片大小，状态码: {get_resp.status_code}")
                    except Exception as err:
                        print(f"获取图片大小时出错: {err}")
                        
    except Exception as e:
        print(f"获取专辑总大小时出错: {e}")
    
    print(f"专辑共有{total_files}个文件")
    return total_size
def main():
    parser = argparse.ArgumentParser(description='Download album using jmcomic.')
    parser.add_argument('--album_id', default=422866, type=str, help='The ID of the album to download')
    parser.add_argument('--github_repo', default=None, type=str, help='GitHub仓库路径，默认为当前目录')
    parser.add_argument('--no_push', action='store_true', help='下载后不推送到GitHub')
    args = parser.parse_args()

    option = jmcomic.create_option_by_file('../option.yml')

    # 下载前先检测专辑所有文件的总大小
    total_size = get_total_size(args.album_id, option)
    total_size_mb = total_size / (1024 * 1024)
    print("总文件大小: {} MB".format(total_size_mb))
    if total_size_mb > 1024:
        print("文件过大 > 1G")
        return

    # 下载album
    print(f"开始下载专辑 {args.album_id}...")
    result = jmcomic.download_album(args.album_id, option)

    # 提取专辑名称，用于提交信息
    album_detail = result[0]  # 通常download_album返回一个元组，第一个元素是专辑详情
    album_name = getattr(album_detail, 'name', f"Album-{args.album_id}")

    # 如果未设置no_push标志，则推送到GitHub
    if not args.no_push:
        push_to_github(args.album_id, album_name, args.github_repo)


if __name__ == '__main__':
    main()