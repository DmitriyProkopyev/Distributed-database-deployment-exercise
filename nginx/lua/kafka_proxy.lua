local cjson = require "cjson"

local request_id = tostring(ngx.now()) .. "-" .. tostring(ngx.worker.pid())

local request_data = {
    method = ngx.req.get_method(),
    uri = ngx.var.request_uri,
    headers = ngx.req.get_headers(),
    request_id = request_id
}

if ngx.req.get_method() == "POST" or ngx.req.get_method() == "PUT" then
    ngx.req.read_body()
    request_data.body = ngx.req.get_body_data()
end

local ok, err = producer:send("nginx_requests", nil, cjson.encode(request_data))
if not ok then
    ngx.log(ngx.ERR, "failed to send to kafka: ", err)
    return ngx.exit(500)
end

ngx.status = 202
ngx.header["Content-Type"] = "application/json"
ngx.say(cjson.encode({
    status = "accepted",
    request_id = request_id,
    message = "Request is being processed"
}))
return ngx.exit(202)
