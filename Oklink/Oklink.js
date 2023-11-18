function getApiKey(API_KEY,l) {
var e = (new Date).getTime()
    , t = encryptApiKey(API_KEY);
return e = encryptTime(e,l),
    comb(t, e)
};

function encryptApiKey(API_KEY) {
    var e = API_KEY
      , t = e.split("")
      , r = t.splice(0, 8);
    return e = t.concat(r).join("")
    }

function encryptTime(e,l) {
    var t = (1 * e + l).toString().split("")
      , r = parseInt(10 * Math.random(), 10)
      , n = parseInt(10 * Math.random(), 10)
      , o = parseInt(10 * Math.random(), 10);
    return t.concat([r, n, o]).join("")
}

function comb(e, t) {
    var r = "".concat(e, "|").concat(t);
    return r
}
