// 云函数入口文件
const cloud = require('wx-server-sdk')
var rp = require('request-promise')

cloud.init()

// 云函数入口函数
exports.main = async (event, context) => {
  // const wxContext = cloud.getWXContext()
  var url = event.url;
  var referer = event.referer;
  // console.log('收到参数url:'+url)
  return await rp({
    url: url,
    method: "GET",
    json: true,
    headers: {
      'referer':referer
    },
  })
  .then(function (res) {
    console.log(res)
    return res
  })
  .catch(function (err) {
    return '请求失败'
  })
}