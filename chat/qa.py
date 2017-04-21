#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP 8 check with Pylint
"""qa

NLU based on Natural Language Processing and Graph Database.
基于自然语言处理与图形数据库的自然语言理解。

Available functions:
- All classes and functions: 所有类和函数
"""

import os
import sys
import codecs
import json
from py2neo import Graph, Node, Relationship
from api import *
from .semantic import synonym_cut, get_tag, similarity, get_musicinfo, get_navigation_target
from .mytools import time_me, get_current_time, random_item


class Robot():
    """NLU Robot.
    自然语言理解机器人。

    Public attributes:
    - graph: The connection of graph database. 图形数据库连接。
    - pattern: The pattern for NLU tool: 'semantic' or 'vec'. 语义标签或词向量模式。
    - memory: The context memory of robot. 机器人对话上下文记忆。
    """
    def __init__(self, configpath=None):
        self.graph = Graph("http://localhost:7474/db/data/", password="train")
        self.pattern = 'semantic'
        self.is_scene = False # 在线场景标志，默认为False
        self.address = get_location_by_ip()["content"]["address"] # 调用百度地图IP定位api
        self.topic = ""
        self.qa_id = get_current_time()
        self.gconfig = None # TODO 在登录时加载
        self.usertopics = []
        # Pre loading concept
        self.do_not_know = ["这个问题太难了，{robotname}还在学习中", "这个问题{robotname}不会，要么我去问下",
            "您刚才说的是什么，可以再重复一遍吗", "{robotname}刚才走神了，一不小心没听清", "{robotname}理解的不是很清楚啦，你就换种方式表达呗","不如我们换个话题吧","咱们聊点别的吧",
            "{robotname}正在学习中", "{robotname}正在学习哦", "不好意思请问您可以再说一次吗", "额，这个问题嘛。。。",
            "{robotname}得好好想一想呢", "请问您说什么", "您问的问题好有深度呀", "{robotname}没有听明白，您能再说一遍吗"]
		# Robot Memory
        self.memory = []

    def __str__(self):
        return "Hello! I'm {robotname} and I'm {age} years old.".format(**self.config)

    @time_me()
    def configure(self, info="", userid="userid"):
        """Configure knowledge base.
        配置知识库。
        """
        assert userid is not "", "The userid can not be empty!"
        usertopics = self.get_usertopics(userid=userid)
        if not info:
            config = {"databases": []}
            match_string = "MATCH (user:User)-[r:has]->(config:Config) where user.userid='" + userid + "' RETURN config.name as name, r.bselected as bselected, r.available as available"
            for item in self.graph.run(match_string):
                config["databases"].append(dict(name=item[0], bselected=item[1], available=item[2]))
            print("可配置信息：", config)
            return config
        else:
            namelist = info.split()
        print("新配置信息：", namelist)
        for name in namelist:
            match_string = "MATCH (user:User)-[r:has]->(config:Config) where user.userid='" + userid + "' AND config.name='" + name + "' SET r.bselected=1"
            # print(match_string)
            self.graph.run(match_string)
        return self.get_usertopics(userid=userid)

    # @time_me()
    def get_usertopics(self, userid="userid"):
        usertopics = []
        if not userid:
            userid = "userid"       
        # 从知识库获取用户拥有权限的子知识库列表
        match_string = "MATCH (user:User)-[r:has {bselected:1, available:1}]->(config:Config) where user.userid='" + userid + "' RETURN config"
        data = self.graph.run(match_string).data()
        usertopics = [item["config"]["topic"] for item in data]
        print("用户：", userid, "\n已有知识库列表：", usertopics)
        return usertopics

    def iformat(self, sentence):
        """Individualization of robot answer.
        个性化机器人回答。
        """
        return sentence.format(**self.gconfig)

    def add_to_memory(self, question="question", userid="userid"):
        """Add user question to memory.
        将用户当前对话加入信息记忆。

        Args:
            question: 用户问题。
                Defaults to "question".
            userid: 用户唯一标识。
                Defaults to "userid".
        """
        self.memory.append(question)
        previous_node = self.graph.find_one("Memory", "qa_id", self.qa_id)
        self.qa_id = get_current_time()
        node = Node("Memory", question=question, userid=userid, qa_id=self.qa_id)
        if previous_node:
            relation_previous = Relationship(node, "previous", previous_node)
            relation_next = Relationship(previous_node, "next", node)
            self.graph.create(relation_previous | relation_next)
        else:
            self.graph.create(node)

    def extract_synonym(self, question, subgraph):
        """Extract synonymous QA in NLU database。
        QA匹配模式：从图形数据库选取匹配度最高的问答对。

        Args:
            question: User question. 用户问题。
            subgraph: Sub graphs corresponding to the current dialogue. 当前对话领域对应的子图。
        """
        temp_sim = 0
        result = dict(question=question, content=self.iformat(random_item(self.do_not_know)), context="", url="", behavior=0, parameter=0)
	    # semantic: 切分为同义词标签向量，根据标签相似性计算相似度矩阵，由相似性矩阵计算句子相似度
	    # vec: 切分为词向量，根据word2vec计算相似度矩阵，由相似性矩阵计算句子相似度
        if self.pattern == 'semantic':
        # elif self.pattern == 'vec':
            sv1 = synonym_cut(question, 'wf')
            if not sv1:
                return result
            for node in subgraph:
                iquestion = self.iformat(node["name"])
                if question == iquestion:
                    print("Similarity Score: Original sentence")
                    print(result)
                    result["content"] = self.iformat(random_item(node["content"].split("|")))
                    result["context"] = node["topic"]
                    if node["url"]:
                        # result["url"] = json.loads(random_item(node["url"].split("|")))
                        result["url"] = random_item(node["url"].split("|"))
                    if node["behavior"]:
                        result["behavior"] = int(node["behavior"], 16)
                    if node["parameter"]:
                        result["parameter"] = int(node["parameter"])
                    # 知识实体节点api抽取原始问题中的关键信息，据此本地查询/在线调用第三方api/在线爬取
                    func = node["api"]
                    if func:
                        # _locals = locals()
                        exec("result['content'] = " + func + "('" + result["content"] + "', " + "question)")#, globals(), _locals)
                        # result = _locals["result"]
                    return result
                sv2 = synonym_cut(iquestion, 'wf')
                if sv2:
                    temp_sim = similarity(sv1, sv2, 'j')
			    # 匹配加速，不必选取最高相似度，只要达到阈值就终止匹配
                if temp_sim > 0.9:
                    print("Q: " + iquestion + " Similarity Score: " + str(temp_sim))
                    result["content"] = self.iformat(random_item(node["content"].split("|")))
                    result["context"] = node["topic"]
                    if node["url"]:
                        # result["url"] = json.loads(random_item(node["url"].split("|")))
                        result["url"] = random_item(node["url"].split("|"))
                    if node["behavior"]:
                        result["behavior"] = int(node["behavior"], 16)
                    if node["parameter"]:
                        result["parameter"] = int(node["parameter"])
                    func = node["api"]
                    if func:
                        # _locals = locals()
                        exec("result['content'] = " + func + "('" + result["content"] + "', " + "question)")#, globals(), _locals)
                        # result = _locals["result"]
                    return result
        return result

    @time_me()
    def search(self, question="question", userid="userid"):
        """Nlu search. 语义搜索。

        Args:
            question: 用户问题。
                Defaults to "question".
            userid: 用户唯一标识。
                Defaults to "userid"

        Returns:
            Dict contains answer, current topic, url, behavior and parameter. 
            返回包含答案，当前话题，资源包，行为指令及对应参数的字典。
        """
        # 云端在线场景
        result = dict(question=question, content="ok", context="basic_cmd", url="", behavior=int("0x0000", 16), parameter=0)
        if "理财产品" in question or "理财" in question:
            result["behavior"] = int("0x1002", 16) # 进入在线场景
            result["question"] = "理财产品" # 重定义为标准问题
            self.is_scene = True # 在线场景标志
        if "退出业务场景" in question or "退出" in question or "返回" in question:
            result["behavior"] = int("0x0020", 16) # 场景退出
            self.is_scene = False
            return result
        if self.is_scene:
            if "上一步" in question or "上一部" in question:
                result["behavior"] = int("0x001D", 16) # 场景上一步
            elif "下一步" in question or "下一部" in question:
                result["behavior"] = int("0x001E", 16) # 场景下一步
            result["content"] = question
            return result

        # self.add_to_memory(question, userid)
        # 本地语义：全图模式
        #tag = get_tag(question)
        #subgraph = self.graph.find("NluCell", "tag", tag)
        #result = self.extract_synonym(question, subgraph)
        
        # 本地语义：场景+全图+用户配置模式
        # 多用户根据userid动态获取对应的配置信息
        self.gconfig = self.graph.find_one("User", "userid", userid)
        self.usertopics = self.get_usertopics(userid=userid)
        
        tag = get_tag(question, self.gconfig)
        subgraph_all = list(self.graph.find("NluCell", "tag", tag)) 
        # subgraph_scene = [node for node in subgraph_all if node["topic"]==self.topic]
        usergraph_all = [node for node in subgraph_all if node["topic"] in self.usertopics]
        usergraph_scene = [node for node in usergraph_all if node["topic"]==self.topic]
        # if subgraph_scene:
        if usergraph_scene:
            result  = self.extract_synonym(question, usergraph_scene)
            if result["context"]:
                self.topic = result["context"]
                return result
        result  = self.extract_synonym(question, usergraph_all)
        # result  = self.extract_synonym(question, subgraph_all)
        self.topic = result["context"]
        # 在线语义
        if not self.topic:
            # 1.音乐(唱一首xxx的xxx)
            if "唱一首" in question or "我想听" in question:
                singer, song = get_musicinfo(question)
                # result["context"] = "music"
                result["behavior"] = int("0x0001", 16)
                result["content"] = "好的，正在准备哦"
                # result["url"] = music_baidu(song=song, singer=singer) # 音乐资源包
            # 2.附近有什么好吃的
            elif "附近" in question or "好吃的" in question:
                result["behavior"] = int("0x001C", 16)
                result["content"] = self.address
            # 3.nlu_tuling(天气)
            elif "天气" in question:
                weather = nlu_tuling(question, loc=self.address)
                result["behavior"] = int("0x0000", 16)
                result["content"] = weather.split(";")[0].split(",")[1]               
                result["context"] = "nlu_tuling"
            # 4.导航
            elif "带我去" in question or "去" in question:
                result["behavior"] = int("0x001B", 16)
                result["content"] = get_navigation_target(info=question)
            # 5.nlu_tuling
            # else:
                # result["content"] = nlu_tuling(question, loc=self.address)
                # result["context"] = "nlu_tuling"
        return result