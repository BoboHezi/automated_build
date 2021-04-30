
## 签名验收后台API接口

1. 登录
```
Request URL: http://192.168.151.31:8084/sys/login
Request Method: POST
```

请求头：
```
common
```

请求数据：
```json
{
    "remember_me":true,
    "username":"hongxiangyuan",
    "password":"hongxiangyuan014"
}
```

响应数据：
```json
{
    "success":true,
    "message":"登录成功",
    "code":200,
    "result":{
        "userInfo":{
            "id":"3db578c81c966746b5d30b65d509d175",
            "username":"hongxiangyuan",
            "realname":"~hongxiangyuan~内部",
            "password":"882c70190b247a78901fd35022840b3f",
            "salt":"jHxagxbp",
            "avatar":null,
            "birthday":null,
            "sex":null,
            "email":null,
            "phone":null,
            "status":1,
            "delFlag":"0",
            "createBy":"develop",
            "createTime":"2022-07-25 10:43:21",
            "updateBy":"admin",
            "updateTime":"2019-11-19 17:27:04",
            "defaultFtpPath":"ftp://upload.droi.com:21/",
            "defaultFtpUsername":"hongxiangyuan",
            "testerCnName":null
        },
        "token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTgyMTIwNDUsInVzZXJuYW1lIjoiaG9uZ3hpYW5neXVhbiJ9.46WObvzCguWpsrYFG1rrU-jPFbk24G6zheAjgXbsbX4"
    },
    "timestamp":1618210245565
}
```

2. 添加机型（机型管理）
```
Request URL: http://192.168.151.31:8084/sv/models/add
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "model":"V10K-EX",
    "userId1":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "id":888,
        "model":"V10K-EX",
        "createTime":"2021-04-12T14:58:28.194",
        "userId1":"3db578c81c966746b5d30b65d509d175",
        "userName":null
    }
}
```

3. 查询机型（机型管理）
```
Request URL: http://192.168.151.31:8084/sv/models/list
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "pageNo":1,
    "pageSize":10,
    "searchParam":{
        "commonField":"V10K"
    },
    "userid":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "pageSize":10,
        "pageNo":1,
        "totalCount":2,
        "totalPage":1,
        "data":[
            {
                "id":887,
                "model":"V10K",
                "createTime":"2021-04-12T14:42:41",
                "userId1":"3db578c81c966746b5d30b65d509d175",
                "userName":"hongxiangyuan"
            },
            {
                "id":888,
                "model":"V10K-EX",
                "createTime":"2021-04-12T14:58:28",
                "userId1":"3db578c81c966746b5d30b65d509d175",
                "userName":"hongxiangyuan"
            }
        ]
    }
}
```

4. 添加方案商（odm）
```
Request URL: http://192.168.151.31:8084/sv/odms/add
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "odm":"XIAOLAJIAO",
    "userId1":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "id":54,
        "odm":"XIAOLAJIAO",
        "createTime":"2021-04-22T16:00:45.503",
        "userId1":"3db578c81c966746b5d30b65d509d175",
        "userName":null
    }
}
```

5. 查询方案商（odm）
```
Request URL: http://192.168.151.31:8084/sv/odms/list
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "pageNo":1,
    "pageSize":10,
    "searchParam":{
        "commonField":"HONGXIANGYUAN"
    },
    "userid":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "pageSize":10,
        "pageNo":1,
        "totalCount":1,
        "totalPage":1,
        "data":[
            {
                "id":24,
                "odm":"HONGXIANGYUAN",
                "createTime":"2018-12-03T09:57:24",
                "userId1":"3db578c81c966746b5d30b65d509d175",
                "userName":"hongxiangyuan"
            }
        ]
    }
}
```

6. 添加项目（项目管理）
```
Request URL: http://192.168.151.31:8084/sv/projects/add
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "brand":"HONGXIANGYUAN",
    "channel":"HONGXIANGYUAN_HONGXIANGYUAN",
    "project":"V10K",
    "userId1":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "id":1117,
        "channel":"HONGXIANGYUAN_HONGXIANGYUAN",
        "brand":"HONGXIANGYUAN",
        "project":"V10K",
        "userId1":"3db578c81c966746b5d30b65d509d175",
        "createTime":"2021-04-12T15:05:24.865",
        "childProject":null,
        "userName":null
    }
}
```

7. 查询项目
```
Request URL: http://192.168.151.31:8084/sv/projects/list
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "pageNo":1,
    "pageSize":10,
    "searchParam":{
        "commonField":"l42_xa_1hd",
        "brand":"DROI",
        "channel":"DROIPCB",
        "project":"1"
    },
    "userid":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "pageSize":10,
        "pageNo":1,
        "totalCount":1,
        "totalPage":1,
        "data":[
            {
                "id":525,
                "channel":"HONGXIANGYUAN_HONGXIANGYUAN",
                "brand":"HONGXIANGYUAN",
                "project":"A900_MT6763O",
                "userId1":"3db578c81c966746b5d30b65d509d175",
                "createTime":"2019-09-16T16:20:36",
                "childProject":null,
                "userName":"hongxiangyuan"
            }
        ]
    }
}
```

8. 添加品牌商
```
Request URL: http://192.168.151.31:8084/sv/brands/add
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "brand":"XIAOLAJIAO",
    "userId1":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "id":103,
        "brand":"XIAOLAJIAO",
        "userId1":"3db578c81c966746b5d30b65d509d175",
        "createTime":"2021-04-22T16:09:20.839",
        "userName":null
    }
}
```

9. 查询品牌商
```
Request URL: http://192.168.151.31:8084/sv/brands/list
Request Method: POST
```

请求头：
```
common-token
```

请求数据：
```json
{
    "pageNo":1,
    "pageSize":10,
    "searchParam":{
        "commonField":"HONGXIANGYUAN"
    },
    "userid":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "pageSize":10,
        "pageNo":1,
        "totalCount":1,
        "totalPage":1,
        "data":[
            {
                "id":55,
                "brand":"HONGXIANGYUAN",
                "userId1":"3db578c81c966746b5d30b65d509d175",
                "createTime":"2018-12-03T09:57:50",
                "userName":"hongxiangyuan"
            }
        ]
    }
}
```

10. 创建验收任务
```
Request URL: http://192.168.151.31:8084/sv/verifytasks/add
Request Method: POST
```

请求头：
```
common
X-Access-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTgyMTIwNDUsInVzZXJuYW1lIjoiaG9uZ3hpYW5neXVhbiJ9.46WObvzCguWpsrYFG1rrU-jPFbk24G6zheAjgXbsbX4
```

请求数据：
```json
{
    "signAndVerify":1,
    "purpose":0,
    "projectId":1117,
    "ftpPath":"ftp://192.168.150.30/download/202103/V10K/V10KA-G1930FUA-ZY-0409-V0104-UNSIGN_signed.zip",
    "ftpUsername":"hongxiangyuan",
    "platform":"SPRD_T310p_hongxiangyuan",
    "board":"V10K",
    "ccList":"zhangzhanbo@droi.com",
    "model":"V10K",
    "brandCustomer":"HONGXIANGYUAN",
    "odmCustomer":"HONGXIANGYUAN",
    "ftpPublishFolder":"ftp://upload.droi.com:21/",
    "ftpPublishUsername":"hongxiangyuan",
    "passby":0,
    "level":null,
    "userName":"hongxiangyuan",
    "userId1":"3db578c81c966746b5d30b65d509d175"
}
```
### 字段说明
| 字段名 | 说明 | eg |
|:---|:---|:---|
|signAndVerify      |签名并验收||
|purpose            |验收用途（0：正式，1：工厂）||
|projectId          |项目ID（项目管理）||
|ftpPath            |签名包地址（签名包目标地址）||
|ftpUsername        |签名包地址用户||
|platform           |签名平台||
|board              |主板||
|ccList             |邮件接受者||
|model              |机型||
|brandCustomer      |品牌商||
|odmCustomer        |方案商||
|ftpPublishFolder   |验收包释放ftp地址|ftp://upload.droi.com:21/|
|ftpPublishUsername |验收包释放用户名||
|passby             |||
|level              |优先级||
|userName           |登录用户名||
|userId1            |登录用户ID||

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "taskId":11992,
        "authenticationCode":null,
        "ftpPath":"ftp://192.168.150.30/download/202103/V10K/V10KA-G1930FUA-ZY-0409-V0104-UNSIGN_signed.zip",
        "ftpUsername":"hongxiangyuan",
        "localPath":null,
        "ftpVerifiedPath":null,
        "ftpVerifiedUsername":null,
        "localVerifiedPath":null,
        "process":0,
        "status":0,
        "errorCode":0,
        "publisher":null,
        "verifyTime":null,
        "jobNumber":null,
        "createTime":"2021-04-12T15:17:16",
        "userName":"hongxiangyuan",
        "userId1":"3db578c81c966746b5d30b65d509d175",
        "queueId":null,
        "testInput":null,
        "publishQueueId":null,
        "ftpPublishPath":null,
        "ftpPublishUsername":"hongxiangyuan",
        "publishJobNumber":null,
        "ftpPublishFolder":"ftp://upload.droi.com:21/",
        "board":"V10K",
        "level":0,
        "brandCustomer":"HONGXIANGYUAN",
        "platform":"SPRD_T310p_hongxiangyuan",
        "projectId":1117,
        "urgentContent":null,
        "ccList":"zhangzhanbo@droi.com",
        "model":"V10K",
        "verifyFailReason":null,
        "imageCustomerBr":null,
        "imageChannelNo":null,
        "imageCustomerNo":null,
        "remarks":null,
        "signAndVerify":1,
        "imageVersion":null,
        "imageBuildTime":null,
        "imageLicense":null,
        "imageProjectName":null,
        "odmCustomer":"HONGXIANGYUAN",
        "purpose":0,
        "verifyChildProject":null,
        "ftpPublishTargetFilesPath":null,
        "projectAdjusted":null,
        "passby":0,
        "sysAvailable":null,
        "cloudPath":null,
        "targetFilesCloudPath":null,
        "otaFtpPath":null,
        "otaStatus":null,
        "obproject":null
    }
}
```

11. 创建签名任务
```
Request URL: http://192.168.151.31:8084/sv/signtasks/add
Request Method: POST
Remote Address: 192.168.151.31:8084
Referrer Policy: strict-origin-when-cross-origin
```

请求头：
```
common
X-Access-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTgyMTIwNDUsInVzZXJuYW1lIjoiaG9uZ3hpYW5neXVhbiJ9.46WObvzCguWpsrYFG1rrU-jPFbk24G6zheAjgXbsbX4
```

请求数据：
```json
{
    "name":"V10KA-G1930FUA-ZY-0409-V0104",
    "urlBefore":"ftp://192.168.150.30/upload/202103/V10K/V10KA-G1930FUA-ZY-0409-V0104-UNSIGN.zip",
    "intro":"commit in sign",
    "model":"V10K-EX",
    "platform":"SPRD_T310p_hongxiangyuan",
    "signAndVerify":1,
    "ftpUsername":"hongxiangyuan",
    "taskId":11993,
    "userId1":"3db578c81c966746b5d30b65d509d175"
}
```
### 字段说明
| 字段名 | 说明 | eg |
|:---|:---|:---|
|name          |名称||
|urlBefore     |签名包地址||
|intro         |备注||
|model         |机型||
|platform      |签名平台||
|signAndVerify |签名并验收||
|ftpUsername   |签名包ftp登录名||
|taskId        |验收ID||
|userId1       |登录用户ID||

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS",
    "data":{
        "id":13919,
        "name":"V10KA-G1930FUA-ZY-0409-V0104",
        "urlBefore":"ftp://192.168.150.30/upload/202103/V10K/V10KA-G1930FUA-ZY-0409-V0104-UNSIGN.zip",
        "pathBefore":null,
        "urlAfter":null,
        "pathAfter":null,
        "status":0,
        "intro":"commit in sign",
        "userId1":"3db578c81c966746b5d30b65d509d175",
        "createTime":"2021-04-12T15:35:13",
        "isOta":null,
        "projects":null,
        "model":"V10K-EX",
        "platform":"SPRD_T310p_hongxiangyuan",
        "signAndVerify":1,
        "taskId":11993,
        "jobNumber":null,
        "errorCode":null,
        "targetFilesCloudPath":null,
        "cloudPath":null,
        "ftpSignedUsername":null,
        "ftpUsername":"hongxiangyuan",
        "queueId":null,
        "verifytask":null,
        "userName":null
    }
}
```

12. 开始任务
```
Request URL: http://192.168.151.31:8084/sv/signtasks/handle
Request Method: POST
Remote Address: 192.168.151.31:8084
Referrer Policy: strict-origin-when-cross-origin
```

请求头：
```
common
X-Access-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTgyMTIwNDUsInVzZXJuYW1lIjoiaG9uZ3hpYW5neXVhbiJ9.46WObvzCguWpsrYFG1rrU-jPFbk24G6zheAjgXbsbX4
```

请求数据：
```json
{
    "taskId":13918,/*签名任务id*/
    "type":10,
    "userid":"3db578c81c966746b5d30b65d509d175"
}
```

响应数据：
```json
{
    "code":1000,
    "msg":"SUCCESS"
}
```

13. 查询信息（info）
```
Request URL: http://192.168.151.31:8084/sv/verifytasks/info
Request Method: POST
```

请求头：
```
common
X-Access-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTgyMTIwNDUsInVzZXJuYW1lIjoiaG9uZ3hpYW5neXVhbiJ9.46WObvzCguWpsrYFG1rrU-jPFbk24G6zheAjgXbsbX4
```

请求数据：
```json
{"id":"3db578c81c966746b5d30b65d509d175"}
```

响应数据：
```json
info.json
```

### common-header
```
Accept: application/json, text/plain, */*,
Accept-Encoding: gzip, deflate,
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,
Connection: keep-alive,
Content-Length: 77,
Content-Type: application/json;charset=UTF-8,
Host: 192.168.151.31:8084,
Origin: http://192.168.151.31:2030,
Referer: http://192.168.151.31:2030/,
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36
```

### common-token-header
```
Accept: application/json, text/plain, */*,
Accept-Encoding: gzip, deflate,
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,
Connection: keep-alive,
Content-Length: 77,
Content-Type: application/json;charset=UTF-8,
Host: 192.168.151.31:8084,
Origin: http://192.168.151.31:2030,
Referer: http://192.168.151.31:2030/,
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36
X-Access-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTk2Nzc2NDYsInVzZXJuYW1lIjoiaG9uZ3hpYW5neXVhbiJ9.9MuBgtToXDtQeAPC3lDHRuFodqfa_ajKBQMpHadPlTQ
```

### 生产服务器地址: http://sign.ttddsh.com:8084
