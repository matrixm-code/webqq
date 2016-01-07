写了一个通过webqq去发送数据库的小程序


目前每次登陆都要手动填写一些信息:
    ptwebqq
    hash
    psessionid
    vfwebqq
    clientid  -这个值不知道是不是可以任意, 不过目前来说确定下来就不能变

有一个数据库结构:
 CREATE TABLE `qq_assistant` (
  `iId` int(8) NOT NULL AUTO_INCREMENT,
  `sType` varchar(10) NOT NULL DEFAULT 'person' COMMENT '发送类型',
  `sTo` int(20) NOT NULL DEFAULT '276949696' COMMENT '接收qq号码',
  `sContents` varchar(2500) NOT NULL DEFAULT '恭喜发财' COMMENT '发送内容',
  `iStatus` int(2) NOT NULL DEFAULT '0' COMMENT '发送状态：0-等待执行，1-成功，2-失败，4-未知错误',
  `dDateCreate` datetime NOT NULL DEFAULT '2016-01-06 01:01:01' COMMENT '创建时间',
  `dDateRun` datetime DEFAULT NULL COMMENT '执行时间',
  `sErrorMsg` varchar(250) DEFAULT NULL COMMENT '错误信息',
  `sOperationUser` varchar(20) NOT NULL DEFAULT 'admin00' COMMENT '操作人',
  PRIMARY KEY (`iId`)
) ENGINE=InnoDB AUTO_INCREMENT=31495 DEFAULT CHARSET=utf8 COMMENT='qq小助手'