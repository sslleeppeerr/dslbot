//校园教务场景DSL

INTENT campus {
    when intent == campus then reply "你好，这里是教务助手，你是要咨询选课还是成绩？";
    when contains "选课" then set topic = "course";
    when contains "成绩" then set topic = "grade";
    when intent == campus then reply "收到，你关注{topic}。请详细描述你的问题。";
}

INTENT fallback{
    //兜底意图
    when always then reply "你好，我是校园助手，可讨论选课、成绩等。请再具体一些~";
}