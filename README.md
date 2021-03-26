# WeChat_server_destiny

本插件仅供学习研究使用，请勿用于商业用途，一切后果自己承担。

python微信公众号后台服务器，命运2相关信息查询。

鸣谢 @seanalpha @天阙 @wenmumu @kamuxiy @两仪未央。

## 使用
* 根据./data/main_data_template.json填入相关内容，proxy可填可不填,改完后改名为main_data.json

* update_interface.py用于更新微信公众号自定义接口，具体配置在./src/interface.py中

* 程序启动启动可使用以下代码：

  ~~~shell
  python3 main.py
  #或者使用脚本（用screen启动）
  ./start.sh
  ~~~

  注：本代码在python3.7.5测试通过

