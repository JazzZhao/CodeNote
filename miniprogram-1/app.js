//引入插件：微信同声传译
const plugin = requirePlugin('WechatSI');
//获取全局唯一的语音识别管理器recordRecoManager
const manager = plugin.getRecordRecognitionManager();
const backgroundAudioManager = wx.getBackgroundAudioManager();

App({
  
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    wx.cloud.init({
      traceUser : true
    })
    
    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
    //创建内部audio上下文
    this.innerAudioContext = wx.createInnerAudioContext()
    this.innerAudioContext.onError(function(res){
      console.log(res);
      wx.showToast({
        title: '语音播放失败',
        icon:'none'
      })
    }),
    //识别语音初始化
    this.initRecord();
  },
  globalData: {
    userInfo: null,
    // 播放列表数据
    playlist: [],
    childplaylist:[]
  },
  //识别语音 -- 初始化
  initRecord: function () {
    const that = this;
    // 有新的识别内容返回，则会调用此事件
    manager.onRecognize = function (res) {
      console.log(res)
    }
    // 正常开始录音识别时会调用此事件
    manager.onStart = function (res) {
      console.log("成功开始录音识别", res)
    }
    // 识别错误事件
    manager.onError = function (res) {
      console.error("error msg", res)
    }
    //识别结束事件
    manager.onStop = function (res) {
      console.log('..............结束录音')
      console.log('录音临时文件地址 -->' + res.tempFilePath); 
      console.log('录音总时长 -->' + res.duration + 'ms'); 
      console.log('文件大小 --> ' + res.fileSize + 'B');
      console.log('语音内容 --> ' + res.result);
      if (res.result == '') {
        // wx.showModal({
        //   title: '提示',
        //   content: '听不清楚，请重新说一遍！',
        //   showCancel: false,
        //   success: function (res) {}
        // })
        // return;
        that.wordYun('听不清楚，请重新说一遍！');
      }else{
        that.getVideoList(res.result)
      }
    }
  },
  //识别语音开始
  recordRecognitionStart: function (params) {
    // 语音开始识别
    manager.start({
      lang: 'zh_CN',// 识别的语言，目前支持zh_CN en_US zh_HK sichuanhua
    })
  },
  //识别语音结束
  recordRecognitionEnd:function (params) {
    // 语音结束识别
    manager.stop();
  },

  // 文字转语音
  wordYun:function (content) {
    var that = this;
    plugin.textToSpeech({
      lang: "zh_CN",
      tts: true,
      content: content,
      success: function (res) {
        console.log(res);
        console.log("succ tts", res.filename);
        that.yuyinPlay(res.filename);
      },
      fail: function (res) {
        console.log("fail tts", res)
      }
    })
  },
  //播放语音
  yuyinPlay: function (src) {
    if (src == '') {
      console.log(暂无语音);
      return;
    }
    this.innerAudioContext.src = src //设置音频地址
    this.innerAudioContext.play(); //播放音频
  },
  // 结束语音
  endPlay: function (e) {
    this.innerAudioContext.pause();//暂停音频
  },
  //结束背景音
  endbackgroundAudio:function (params) {
    backgroundAudioManager.stop();
  },

  searchDb:function (input) {
    var that = this
    const db = wx.cloud.database({});
    db.collection('video_name').where({
      title:{
        $regex:'.*'+input+'.*',
        $options:'5'
      }
    })
    .get({
      success: function(res) {
        // res.data 是包含以上定义的两条记录的数组
        if(res.data.length == 0){
          that.getVideoList(input)
        }else{
          that.globalData.playlist = res.data
          wx.navigateTo({
            url: '../playlist/playlist'
          })
        }
      }
    })
  },

  //影视部分
  getVideoList:function(input){
    var that = this
    input = input.replace(/\(|\)|\;|\,|\。/g,'')
    input = encodeURIComponent(input)
    console.log(input)
    //7秒提醒用户一次正在搜索
    var interval = setInterval(function () {
      clearInterval(interval);//关闭定时任务
      that.wordYun('正在搜索资源，您稍等！');
    }, 7000)
    wx.cloud.callFunction({
      name:'video_search',
      data:{
        url:'https://www.qiuziyuan.net/vip/api.php?out=jsonp&wd='+input,
        referer:"https://www.qiuziyuan.net/vip/so.php?wd="+input,
      }
    }).then((res)=>{
      clearInterval(interval);//关闭定时任务
      var result = res.result
      result = result.replace(/\(|\)|\;/g,'')
      result = JSON.parse(result);
      if(result.code == 0){
        console.log(result)
        var tmplist = []
        for(var i=0; i<result.info.length; i++){
          var tmp = {
            id: result.info[i].id,
            title: result.info[i].title,
            flag: result.info[i].flag,
            src: '',
            coverImgUrl: result.info.img
          }
          tmplist.push(tmp)
        }
        this.globalData.playlist = tmplist
        //置空
        this.globalData.childplaylist = []
        wx.navigateTo({
          url: '../playlist/playlist'
        })
      }else{
        that.wordYun('没有搜到资源，您说点别的试试！');
      }
    }).catch(err =>{
      that.wordYun('没有搜到资源，您说点别的试试！');
    });
  },

})
