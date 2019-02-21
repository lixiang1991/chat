API - 语义知识库管理 API 接口
================================================

.. image:: my_figs/kmapi.ico
  :scale: 50 %

.. automodule:: kmapi

.. autosummary::

   kmapi.allowed_file
   kmapi.get_username
   kmapi.get_available_kb
   kmapi.get_selected_kb
   root_data
   signin
   signout
   get_skb
   user_edit
   scene_error
   reset
   upload
   upload_img
   download_img
   download
   config_manage
   config_add
   config_delete
   config_delete_admin
   search_nlucell
   search_scene
   nlucell_item
   nlucell_add
   nlucell_edit
   nlucell_delete
   scene_topic
   scene_item
   scene_add
   scene_edit
   scene_delete
   scene_add_single
   scene_edit_single
   scene_delete_single
   start

判断文件类型是否允许
------------------------------------------------
.. autofunction:: kmapi.allowed_file

获取 chatbot 名字
------------------------------------------------
.. autofunction:: kmapi.get_username

获取可用的知识库列表
------------------------------------------------
.. autofunction:: kmapi.get_available_kb

获取已启用的知识库列表
------------------------------------------------
.. autofunction:: kmapi.get_selected_kb

获取数据资源引用路径
------------------------------------------------
.. autofunction:: root_data

登录
------------------------------------------------
.. autofunction:: signin

退出
------------------------------------------------
.. autofunction:: signout

获取当前知识库名称
------------------------------------------------
.. autofunction:: get_skb

编辑用户信息
------------------------------------------------
.. autofunction:: user_edit

场景 error_page
------------------------------------------------
.. autofunction:: scene_error

重置用户所有已有知识库
------------------------------------------------
.. autofunction:: reset

上传知识库
------------------------------------------------
.. autofunction:: upload

上传图片
------------------------------------------------
.. autofunction:: upload_img

下载图片
------------------------------------------------
.. autofunction:: download_img

下载知识库
------------------------------------------------
.. autofunction:: download

知识库配置
------------------------------------------------
.. autofunction:: config_manage

添加知识库
------------------------------------------------
.. autofunction:: config_add

用户删除知识库
------------------------------------------------
.. autofunction:: config_delete

管理员删除知识库
------------------------------------------------
.. autofunction:: config_delete_admin

搜索问答节点
------------------------------------------------
.. autofunction:: search_nlucell

搜索场景节点
------------------------------------------------
.. autofunction:: search_scene

获取问答节点列表
------------------------------------------------
.. autofunction:: nlucell_item

添加问答节点
------------------------------------------------
.. autofunction:: nlucell_add

编辑问答节点
------------------------------------------------
.. autofunction:: nlucell_edit

删除问答节点
------------------------------------------------
.. autofunction:: nlucell_delete

返回当前所选知识库所有场景根节点
------------------------------------------------
.. autofunction:: scene_topic

获取场景节点列表
------------------------------------------------
.. autofunction:: scene_item

添加场景节点
------------------------------------------------
.. autofunction:: scene_add

编辑场景节点
------------------------------------------------
.. autofunction:: scene_edit

删除场景节点及其所有子节点
------------------------------------------------
.. autofunction:: scene_delete

添加单节点场景
------------------------------------------------
.. autofunction:: scene_add_single

编辑单节点场景
------------------------------------------------
.. autofunction:: scene_edit_single

删除单节点场景
------------------------------------------------
.. autofunction:: scene_delete_single

启动知识库管理服务
------------------------------------------------
.. autofunction:: start
