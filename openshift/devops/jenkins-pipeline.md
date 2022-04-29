# OpenShift 4 基于Gogs+Nexus+Sonarqube的Jenkins CI/CD Pipeline

说明：本文已经在 OpenShift 4.8 环境中验证（OpenShift 4.9 环境的 Jenkins 版本较新，编译 Java 报错）

## OpenShift 4之实现一个基于Gogs+Nexus+Sonarqube的Jenkins CI/CD Pipeline

### 准备运行所需要的资源

1. 新建三个项目，分别是运行Jenkins的CICD项目，以及开发（Dev）和准上线环境（Stage）。

```bash
export USER_ID=adam
oc new-project ${USER_ID}-cicd
oc new-project ${USER_ID}-dev
oc new-project ${USER_ID}-stage
```

2. 用管理员用户执行命令，允许从USER-ID-cicd项目访问另外两个项目的资源。
```bash
oc policy add-role-to-group edit system:serviceaccounts:${USER_ID}-cicd -n ${USER_ID}-dev
oc policy add-role-to-group edit system:serviceaccounts:${USER_ID}-cicd -n ${USER_ID}-stage
```

3. xxx
```bash
# oc create -f https://raw.githubusercontent.com/liuxiaoyu-git/OpenShift-HOL/master/Maven-Gogs-Sonar-Pipeline-Template.yaml -n openshift
curl -sL -o Maven-Gogs-Sonar-Pipeline-Template.yaml https://raw.githubusercontent.com/liuxiaoyu-git/OpenShift-HOL/master/Maven-Gogs-Sonar-Pipeline-Template.yaml
oc create -f Maven-Gogs-Sonar-Pipeline-Template.yaml -n openshift

oc new-app --template=jenkins-ephemeral -n ${USER_ID}-cicd 
oc new-app --template=cicd -n ${USER_ID}-cicd -p DEV_PROJECT=${USER_ID}-dev -p STAGE_PROJECT=${USER_ID}-stage
```


创建cicd模板遇到问题:
Using non-groupfied API resources is deprecated and will be removed in a future release
解决方法: 把v1改为template.openshift.io/v1

13. 执行命令获得Jenkins、Gogs、Nexus和SonarQube的控制台访问地址，并设置到环境变量中。

```bash
GOGS=http://$(oc get route gogs -n ${USER_ID}-cicd -o template --template '{{.spec.host}}')
JENKINS=https://$(oc get route jenkins -n ${USER_ID}-cicd -o template --template '{{.spec.host}}')
NEXUS=http://$(oc get route nexus -n ${USER_ID}-cicd -o template --template '{{.spec.host}}')
SONARQUBE=https://$(oc get route sonarqube -n ${USER_ID}-cicd -o template --template '{{.spec.host}}')
```

### 配置Gogs并导入应用代码

为了能让Jenkins从Gogs获取应用代码，我们先需要将应用代码导入到Gogs。

* 1.访问gogs控制台，在首页面右上方点击“登录”链接，用gogs/gogs登录。
* 2.登陆后点击页面右上方“+”图标，然后在下拉菜单中选择“迁移外部仓储”。
* 3.在“克隆地址”栏中填https://github.com/liuxiaoyu-git/openshift-tasks，然后在“仓库名称”填openshift-tasks，最后点击“迁移仓储”。成功会看到gogs/openshift-tasks的Repository和相关应用代码。

## 参考资料

* [OpenShift 4 Hands-on Lab (7) - 用Jenkins Pipeline实现在不同运行环境中升迁部署应用](https://blog.csdn.net/weixin_43902588/article/details/104285933)
* [OpenShift 4 Hands-on Lab (8) 基于Gogs+Nexus+Sonarqube的Jenkins CI/CD Pipeline ](https://blog.csdn.net/weixin_43902588/article/details/104407106)
* [OpenShift 4 - DevSecOps Workshop (Jenkins版)](https://blog.csdn.net/weixin_43902588/article/details/119963225)
