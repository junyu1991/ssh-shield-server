
/**
* 网站用户
*/
create table user (
    userID varchar(32) primary key auto_increment,
    username varchar(32) not null,
    password varchar(126) not null,
    createTime datetime not null default now(),
    modifyTime datetime not null default now()
);

/**
* 可登录的ssh server
*/
create table host (
    id integer primary key auto_increment,
    host varchar(32) not null,
    hostname varchar(32),
    port integer not null default 22
);
/**
* ssh server登录配置项
*/
create table sshServerConfig (
    id integer primary key auto_increment,
    username varchar(32) not null,
    hostID integer not null
);

/*
* 网站登录日志
*/
create table loginRecord (
    id integer primary key,
    loginid varchar(32) not null,
    logintime datetime not null default now(),
    loginhost varchar(32) not null,
    loginport integer not null,
    createtime datetime not null default now()
);

/**
* ssh登录日志
*/
create table sshLoginRecord(
    id integer primary key,
    loginhostid integer not null,
    sshUserName varchar(32) not null,
    sshLoginTime datetime not null default now(),
    sshLogOffTime datetime not null default now(),
    loginUserID integer not null
);

create table blackList (
    id integer primary key,
    loginHost varchar(32) not null,
    loginUserName varchar(32) not null,
    createTime datetime not null default now()
);

insert into user (username, password) values ('admin', password('admin'));