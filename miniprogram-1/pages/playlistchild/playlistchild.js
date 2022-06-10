// pages/playlistchild/playlistchild.js

const app = getApp();
Page({

  /**
   * 页面的初始数据
   */
  data: {
    childplaylist:[{
      id: 1,
      title: '我的天空',
      singer: '南征北战',
      src: 'http://localhost:3000/1.mp3',
      coverImgUrl: '',
      flag:''
    }]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    var that = this
    that.setData({
      childplaylist : app.globalData.childplaylist
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

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

  // 播放列表换曲功能
  change:function(e){
    var searchRes = this.data.childplaylist[e.currentTarget.dataset.index]
    console.log(searchRes)
    if(searchRes.src !=''){
      wx.navigateTo({
        url: '../player/player?videourl='+searchRes.src,
      })
    }
  },
})