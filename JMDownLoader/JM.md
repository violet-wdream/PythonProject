[hect0x7/JMComic-Crawler-Python: Python API for JMComic | 提供Python API访问禁漫天堂，同时支持网页端和移动端 | 禁漫天堂GitHub Actions下载器🚀](https://github.com/hect0x7/JMComic-Crawler-Python)

### 构思

- 从QQ群接收消息：指定格式

- @robot download 114514

- 项目将数字114514作为参数执行命令

  ```bash
  python main.py --album_id 114514
  ```

- 下载到本地后所有章节会合并成一个pdf





### 新建空项目

pycharm新建空项目

### 命令行下载

```bash
pip install jmcomic -i https://pypi.org/project -U
```

### 获取默认option参数

```python
from jmcomic import JmOption
JmOption.default().to_file('./option.yml') # 创建默认option，导出为option.yml文件
```

所有的参数，可选

```yml
# 开启jmcomic的日志输出，默认为true
# 对日志有需求的可进一步参考文档 → https://jmcomic.readthedocs.io/en/latest/tutorial/11_log_custom/
log: true

# 配置客户端相关
client:
  # impl: 客户端实现类，不配置默认会使用JmModuleConfig.DEFAULT_CLIENT_IMPL
  # 可配置:
  #  html - 表示网页端
  #  api - 表示APP端
  # APP端不限ip兼容性好，网页端限制ip地区但效率高
  impl: html

  # domain: 域名配置，默认是 []，表示运行时自动获取域名。
  # 可配置特定域名，如下：
  # 程序会先用第一个域名，如果第一个域名重试n次失败，则换下一个域名重试，以此类推。
  domain:
    - jm-comic.org
    - jm-comic2.cc
    - 18comic.vip
    - 18comic.org

  # retry_times: 请求失败重试次数，默认为5
  retry_times: 5

  # postman: 请求配置
  postman:
    meta_data:
      # proxies: 代理配置，默认是 system，表示使用系统代理。
      # 以下的写法都可以:
      # proxies: null # 不使用代理
      # proxies: clash
      # proxies: v2ray
      # proxies: 127.0.0.1:7890
      # proxies:
      #   http: 127.0.0.1:7890
      #   https: 127.0.0.1:7890
      proxies: system

      # cookies: 帐号配置，默认是 null，表示未登录状态访问JM。
      # 禁漫的大部分本子，下载是不需要登录的；少部分敏感题材需要登录才能看。
      # 如果你希望以登录状态下载本子，最简单的方式是配置一下浏览器的cookies，
      # 不用全部cookies，只要那个叫 AVS 就行。
      # 特别注意！！！(https://github.com/hect0x7/JMComic-Crawler-Python/issues/104)
      # cookies是区分域名的：
      # 假如你要访问的是 `18comic.vip`，那么你配置的cookies也要来自于 `18comic.vip`，不能配置来自于 `jm-comic.club` 的cookies。
      # 如果你发现配置了cookies还是没有效果，大概率就是你配置的cookies和代码访问的域名不一致。
      cookies:
        AVS: qkwehjjasdowqeq # 这个值是乱打的，不能用

# 下载配置
download:
  cache: true # 如果要下载的文件在磁盘上已存在，不用再下一遍了吧？默认为true
  image:
    decode: true # JM的原图是混淆过的，要不要还原？默认为true
    suffix: .jpg # 把图片都转为.jpg格式，默认为null，表示不转换。
  threading:
    # image: 同时下载的图片数，默认是30张图
    # 数值大，下得快，配置要求高，对禁漫压力大
    # 数值小，下得慢，配置要求低，对禁漫压力小
    # PS: 禁漫网页一次最多请求50张图
    image: 30
    # photo: 同时下载的章节数，不配置默认是cpu的线程数。例如8核16线程的cpu → 16.
    photo: 16



# 文件夹规则配置，决定图片文件存放在你的电脑上的哪个文件夹
dir_rule:
  # base_dir: 根目录。
  # 此配置也支持引用环境变量，例如
  # base_dir: ${JM_DIR}/下载文件夹/
  base_dir: D:/a/b/c/

  # rule: 规则dsl。
  # 本项只建议了解编程的朋友定制，实现在这个类: jmcomic.jm_option.DirRule
  # 写法:
  # 1. 以'Bd'开头，表示根目录
  # 2. 文件夹每增加一层，使用 '_' 或者 '/' 区隔
  # 3. 用Pxxx或者Ayyy指代文件夹名，意思是 JmPhotoDetail.xxx / JmAlbumDetail的.yyy。xxx和yyy可以写什么需要看源码。
  # 
  # 下面演示如果要使用禁漫网站的默认下载方式，该怎么写:
  # 规则: 根目录 / 本子id / 章节序号 / 图片文件
  # rule: 'Bd  / Aid   / Pindex'
  # rule: 'Bd_Aid_Pindex'

  # 默认规则是: 根目录 / 章节标题 / 图片文件
  rule: Bd_Ptitle
```

### 用命令行导入参数

```python
import argparse
import jmcomic

def main():
    parser = argparse.ArgumentParser(description='Download album using jmcomic.')
    parser.add_argument('--album_id', type=str, help='The ID of the album to download')
    args = parser.parse_args()

    option = jmcomic.create_option_by_file('option.yml')
    jmcomic.download_album(args.album_id, option)  # 传入要下载的album的id，即可下载整个album到本地.

if __name__ == '__main__':
    main()
```



### 查看支持的插件

通过代码

```python
from jmcomic import JmOptionPlugin

def list_supported_plugins():
    plugins = [cls.__name__ for cls in JmOptionPlugin.__subclasses__()]
    return plugins

if __name__ == '__main__':
    supported_plugins = list_supported_plugins()
    print("Supported plugins:", supported_plugins)
```

或者查看[插件源码](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/src/jmcomic/jm_plugin.py)

```python
Supported plugins: ['JmLoginPlugin', 'UsageLogPlugin', 'FindUpdatePlugin', 'ZipPlugin', 'ClientProxyPlugin', 'ImageSuffixFilterPlugin', 'SendQQEmailPlugin', 'LogTopicFilterPlugin', 'AutoSetBrowserCookiesPlugin', 'FavoriteFolderExportPlugin', 'ConvertJpgToPdfPlugin', 'Img2pdfPlugin', 'LongImgPlugin', 'JmServerPlugin', 'SubscribeAlbumUpdatePlugin', 'SkipPhotoWithFewImagesPlugin', 'DeleteDuplicatedFilesPlugin', 'ReplacePathStringPlugin']
```

选择需要的插件，在option.yml中plugins选项添加

具体使用方法[配置文件指南 - jmcomic](https://jmcomic.readthedocs.io/zh-cn/latest/option_file_syntax/)

需要注意的是

```yml
plugins:
  after_init:
    - plugin: usage_log # 实时打印硬件占用率的插件
      kwargs:
        interval: 0.5 # 间隔时间
        enable_warning: true # 占用过大时发出预警
```

` - plugin: usage_log # 实时打印硬件占用率的插件`

这里最前面的短横线是必须的

运行项目查看效果

![image-20250324174837110](https://cdn.jsdelivr.net/gh/violet-wdream/Drawio/PNG/202503241748177.png)

如果你的项目缺少了依赖库，命令行应该会输出相应的提示，如果插件的作者考虑到了的话，比如我使用了img2pdf，但是没有安装依赖库

![image-20250324175126553](https://cdn.jsdelivr.net/gh/violet-wdream/Drawio/PNG/202503241751581.png)

