// pages/playlist/playlist.js
const musicTool = require("../../utils/QQMusicPlugin/qqMusicTools.js")
const app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    playlist: [],
    
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    var that = this
    that.setData({
      playlist : app.globalData.playlist
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

  //音乐部分
  getMusicList:function(){
    const that = this;
    musicTool.searchMusic(100, that.data.content).then(function(searchRes) {
      var tmplist = []
      for(var i=0; i<searchRes.length; i++){
        var tmp = {
          id: searchRes[i].id,
          title: searchRes[i].name,
          singer: searchRes[i].artists[0].name,
          src: '',
          coverImgUrl: searchRes[i].artists[0].img1v1Url
        }
        tmplist.push(tmp)
      }
      that.setData({
        playlist:tmplist,
      })

    })
  },
  // 播放列表换曲功能
  change:function(e){
    const that = this;
    var searchRes = this.data.playlist[e.currentTarget.dataset.index]
    console.log(searchRes.playlist)
    if(searchRes.src !=''){
      wx.navigateTo({
        url: '../player/player?videourl='+searchRes.src,
      })
    }else if(searchRes.playlist != undefined && searchRes.playlist.length >0){
      app.globalData.childplaylist= searchRes.playlist
      wx.navigateTo({
        url: '../playlistchild/playlistchild'
      })
    }else{
      id = searchRes.id
      flag = searchRes.flag
      wx.cloud.callFunction({
        name:'video_search',
        data:{
          url:'https://www.qiuziyuan.net/vip/api.php?out=jsonp&flag='+flag+'&id='+id,
          referer:"https://www.qiuziyuan.net/vip/?index20801-4-1.htm",
        }
      }).then((res)=>{
        var result = res.result
        result = result.replace(/\(|\)|\;/g,'')
        result = JSON.parse(result);
        if(result.code == 200){
          console.log(result)
          var tmplist = []
          for(var i=0; i<result.info.length; i++){
            for(var j=0; j<result.info[i].video.length; j++){
              var tmp = {
                title: result.info[i].video[j].split('$')[0],
                src: result.info[i].video[j].split('$')[1],
              }
              tmplist.push(tmp)
            }
          }
          app.globalData.childplaylist= tmplist
          wx.navigateTo({
            url: '../playlistchild/playlistchild'
          })
        }
      }).catch(err =>{
        app.wordYun('搜索的有点慢或者没有资源，您可以重新说一遍！');
      });
    }
    
    //视频播放
    //请求视频地址
    //放入将地址放到data中

    //音乐播放
    // musicTool.playMusic(searchRes.id).then(function(res){
    //   backgroundAudioManager.title = searchRes.title
    //   backgroundAudioManager.epname = searchRes.title
    //   backgroundAudioManager.coverImgUrl = searchRes.coverImgUrl
    //   backgroundAudioManager.singer = searchRes.singer
    //   // 设置了 src 之后会自动播放
    //   backgroundAudioManager.src = res.url
    // })
    // that.setData({
    //   isShowSelectList:false
    // })
  },
})