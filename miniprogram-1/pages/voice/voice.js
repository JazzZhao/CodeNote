// pages/voice/voice.js
const app = getApp();
//引入插件：微信同声传译
const plugin = requirePlugin('WechatSI');
//获取全局唯一的语音识别管理器recordRecoManager
const manager = plugin.getRecordRecognitionManager();
const musicTool = require("../../utils/QQMusicPlugin/qqMusicTools.js")
const backgroundAudioManager = wx.getBackgroundAudioManager()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    handle: false,
    content:'你好，我的朋友，我是小龙',
    src:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    //识别语音
    this.initRecord();
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {
    //创建内部audio上下文
    this.innerAudioContext = wx.createInnerAudioContext()
    this.innerAudioContext.onError(function(res){
      console.log(res);
      wx.showToast({
        title: '语音播放失败',
        icon:'none'
      })
    })
    //文字转语音(欢迎语)
    var that = this;
    that.wordYun();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {
    backgroundAudioManager.stop();
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  //按钮
  buttonHandel: function(event){
    backgroundAudioManager.stop();
    var text = event.currentTarget.dataset.value;
    console.log(text)
    this.setData({
        content: text
      })
    this.wordYun();
  },

  //按住按钮
  startHandel: function () {
    backgroundAudioManager.stop();
    // 语音开始识别
    manager.start({
      lang: 'zh_CN',// 识别的语言，目前支持zh_CN en_US zh_HK sichuanhua
    })
  },
  //松开按钮
  endHandle: function () {
    // 语音结束识别
    manager.stop();
  },

  // 文字转语音
  wordYun:function (e) {
    var that = this;
    var content = this.data.content;
    plugin.textToSpeech({
      lang: "zh_CN",
      tts: true,
      content: content,
      success: function (res) {
        console.log(res);
        console.log("succ tts", res.filename);
        that.setData({
          src: res.filename
        })
        that.yuyinPlay();
      },
      fail: function (res) {
        console.log("fail tts", res)
      }
    })
  },
  //播放语音
  yuyinPlay: function (e) {
    if (this.data.src == '') {
      console.log(暂无语音);
      return;
    }
    this.innerAudioContext.src = this.data.src //设置音频地址
    this.innerAudioContext.play(); //播放音频
  },
 
  // 结束语音
  end: function (e) {
    this.innerAudioContext.pause();//暂停音频
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
      var text = '';
      if (res.result == '') {
        // wx.showModal({
        //   title: '提示',
        //   content: '听不清楚，请重新说一遍！',
        //   showCancel: false,
        //   success: function (res) {}
        // })
        // return;
        text = '听不清楚，请重新说一遍！'
      }else{
          text = res.result
      }
      that.setData({
        content: text
      })
      // that.wordYun();
      that.playmusic()
    }
  },

  //音乐部分
  playmusic:function(){
    const that = this;
    musicTool.searchMusic(1, that.data.content).then(function(searchRes) {
      musicTool.playMusic(searchRes.id).then(function(res){
        backgroundAudioManager.title = searchRes.name
        backgroundAudioManager.epname = searchRes.name
        // // 设置了 src 之后会自动播放
        backgroundAudioManager.src = res.url
      })
    })
  }
})