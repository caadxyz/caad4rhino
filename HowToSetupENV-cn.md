有些用户会发现Caad4rhino没法加载， 这主要是rhino的python环境没有设置好。

windos环境下可以通过一下方式解决：

第一步 确认python环境是否正常

* 打开rhino
* 点击 菜单 Tools-> PythonScript->Edit
* 点击 菜单 File-> New ->Command
* command栏输入 Helloworld
* plugin栏输入 Helloworld
* 点击绿色的Run
* 点击saveall 按钮
* 关闭rhino并重启

第二步 加载python环境

* 打开rhino
* 点击 菜单 Tools-> PythonScript->Edit
* 点击 菜单 File-> Open, 打开 Helloworld_cmd.py
* 点击绿色的Run
* 关闭Rhino python editor
* command栏输入 Helloworld

如果以上执行正常，那么你的python环境是正常加载的。
在执行第二步的时候如果不行 , 可以稍微等一下,  rhino加载需要时间, 或者重新执行一下第二步.   

第三步 安装Caad4Rhino

* 打开rhino
* 点击 菜单 File-> Open, 打开 Helloworld_cmd.py
* 点击save as 按钮 查看文件夹的位置  %AppData%\McNeel\Rhinoceros\6.0\Plug-ins\PythonPlugins\Helloworld {058e2284-c977-4a3a-a188-d2f62ac95e66}
* 把%APPDATA%\McNeel\Rhinoceros\6.0\Plug-ins\PythonPlugIns\caad4rhino{417c9034-2152-48dc-b487-29b584c473a5} 安装在相同的文件夹  %AppData%\McNeel\Rhinoceros\6.0\Plug-ins\PythonPlugins\ 下面
* 关闭rhino并重启
* 如果这次你能执行 Helloworld 命令， 你应该也能执行 caad 命令
