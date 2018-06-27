#! /bin/python
# -*-coding:utf-8 -*-

__author__ = 'Jeson <jisong.zhang@live.cn>'

import commands
import os
import sys


def show_help():
    print 'usage like: python MavenDownloader.py org.json:json:20180130 com.google.code.gson:gson:2.8.5'


def check_arguments():
    if len(sys.argv) <= 1:
        show_help()
        exit(1)


def get_maven_stub():
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
        <dependencies>
            <dependency>
                <groupId>%(group)s</groupId>
                <artifactId>%(name)s</artifactId>
                <version>%(version)s</version>
            </dependency>
        </dependencies>
    </project>"""


def parse_maven_repo():
    maven_repos = []
    for index in range(1, len(sys.argv)):
        arg = sys.argv[index]
        if not arg:
            print "invalid maven repo: %s" % arg
            continue
        maven_arg = arg.split(":")
        if not maven_arg or len(maven_arg) < 3:
            print "invalid maven repo: %s" % arg
            continue
        maven_repos.append({"group": maven_arg[0], "name": maven_arg[1], "version": maven_arg[2]})
    return maven_repos


def create_tmp_pom_file(cur_dir, maven_repo):
    dir_format = "%s/%s.%s.%s" % (cur_dir, maven_repo["group"], maven_repo["name"], maven_repo["version"])
    if not os.path.exists(dir_format):
        os.makedirs(dir_format)
    file_format = "{}/pom.xml".format(dir_format)
    with open(file_format, 'w') as pom:
        content = get_maven_stub() % maven_repo
        pom.write(content)
    return dir_format


def exe_mvn_download(dst_dir):
    os.chdir(dst_dir)
    cmd = ' mvn -f pom.xml dependency:copy-dependencies'
    status, result = commands.getstatusoutput(cmd)
    if result:
        print result
    return status


def start_work():
    check_arguments()
    cur_dir = os.getcwd()
    maven_repos = parse_maven_repo()
    if not maven_repos:
        show_help()
    for maven_repo in maven_repos:
        dst_dir = create_tmp_pom_file(cur_dir, maven_repo)
        status = exe_mvn_download(dst_dir)
        if status != 0:
            print "download maven repo failed: %s:%s:%s" % (
                maven_repo["group"], maven_repo["name"], maven_repo["version"])
        else:
            print "download maven repo success: %s:%s:%s" % (
                maven_repo["group"], maven_repo["name"], maven_repo["version"])


if __name__ == '__main__':
    start_work()
