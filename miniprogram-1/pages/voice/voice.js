// pages/voice/voice.js
var app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    inputShowed: false,  //初始文本框不显示内容
    inputValue:""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {
    //文字转语音(欢迎语)
    app.wordYun('你好，我的朋友，我是小龙');
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
    // backgroundAudioManager.stop();
    var text = event.currentTarget.dataset.value;
    console.log(text)
    app.wordYun(text);
  },

  //按住按钮
  startHandel: function (e) {
    // backgroundAudioManager.stop();
    app.recordRecognitionStart()
  },
  //松开按钮
  endHandle: function () {
    app.recordRecognitionEnd()
  },
  // 使文本框进入可编辑状态
  showInput: function () {
    this.setData({
      inputShowed: true   //设置文本框可以输入内容
    });
  },
  // 取消搜索
  hideInput: function () {
    this.setData({
      inputShowed: false
    });
  },
  //搜索
  search:function (params) {
    app.searchDb(params.detail.value)
  }
})