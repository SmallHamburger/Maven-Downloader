#! /bin/python
# -*-coding:utf-8 -*-

__author__ = 'Jeson <zhangjisong@live.cn>'

import commands
import os
import sys


def show_help():
    print 'usage like: python MavenDownloader.py org.json:json:20180130 com.google.code.gson:gson:2.8.5'


def check_arguments():
    if len(sys.argv) <= 1:
        show_help()
        exit(1)


def get_maven_project_stub():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <project 
        xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
        http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>
        <groupId>maven.download</groupId>
        <artifactId>maven-download</artifactId>
        <version>1.0</version> 
        <repositories>
            %(repos)s
            <repository>
                <id>mavenCentral</id>
                <url>http://central.maven.org/maven2/</url>
            </repository>
        </repositories>
        <dependencies>
            <dependency>
                <groupId>%(group)s</groupId>
                <artifactId>%(name)s</artifactId>
                <version>%(version)s</version>
            </dependency>
        </dependencies>
    </project>"""


def get_maven_repo_stub():
    return """<repository>
                <id>%(name)s</id>
                <url>%(url)s</url>
            </repository>"""


def parse_maven_repo_and_artifact():
    maven_repos = []
    maven_artifacts = []
    for index in range(1, len(sys.argv)):
        arg = sys.argv[index]
        if not arg:
            print "invalid maven repo: %s" % arg
            continue
        if arg.startswith("--repo="):
            arg = arg.replace("--repo=", "")
            repos_array = arg.split(",")
            if not repos_array:
                continue
            for repo in repos_array:
                if not repo:
                    continue
                repo_item = repo.split(":", 1)
                if not repo_item or len(repo_item) < 2:
                    continue
                if not repo_item[0] or not repo_item[1]:
                    continue
                maven_repos.append({"name": repo_item[0], "url": repo_item[1]})
            continue
        maven_arg = arg.split(":")
        if not maven_arg or len(maven_arg) < 3:
            print "invalid maven repo: %s" % arg
            continue
        maven_artifacts.append({"group": maven_arg[0], "name": maven_arg[1], "version": maven_arg[2]})
    return maven_artifacts, maven_repos


def create_tmp_pom_file(cur_dir, maven_artifact, maven_repos):
    work_dir = "%s/%s/%s/%s" % (cur_dir, maven_artifact["group"], maven_artifact["name"], maven_artifact["version"])
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    pom_file = "{}/pom.xml".format(work_dir)
    repo_content_stub = get_maven_repo_stub()
    repo_content = ""
    if maven_repos:
        for repo in maven_repos:
            repo_content = repo_content + (repo_content_stub % repo)
    with open(pom_file, 'w') as pom:
        maven_artifact["repos"] = repo_content
        content = get_maven_project_stub() % maven_artifact
        pom.write(content)
    return work_dir


def exe_mvn_download(dst_dir):
    os.chdir(dst_dir)
    cmd = ' mvn -f pom.xml dependency:copy-dependencies'
    status, result = commands.getstatusoutput(cmd)
    if result:
        print result
    return status


def start_work():
    check_arguments()
    cur_dir = os.getcwd() + "/artifacts"
    maven_artifacts, maven_repos = parse_maven_repo_and_artifact()
    if not maven_artifacts:
        show_help()
    for maven_artifact in maven_artifacts:
        dst_dir = create_tmp_pom_file(cur_dir, maven_artifact, maven_repos)
        status = exe_mvn_download(dst_dir)
        if status != 0:
            print "download maven repo failed: %s:%s:%s" % (
                maven_artifact["group"], maven_artifact["name"], maven_artifact["version"])
        else:
            print "download maven repo success: %s:%s:%s" % (
                maven_artifact["group"], maven_artifact["name"], maven_artifact["version"])


if __name__ == '__main__':
    start_work()
