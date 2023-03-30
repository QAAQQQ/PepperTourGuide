-module(handler).
-export([do/1]).
-include_lib("inets/include/httpd.hrl").

respond(Code, Msg) ->
  Headers = [
    {code, Code},
    {"Access-Control-Allow-Origin", "*"},
    {content_length, integer_to_list(length(Msg))}],
  {break, [{response, {response, Headers, Msg}}]}.
  %{break, [{response, {Code, Msg}}]}.


do(#mod{request_uri="/floor", method="GET"}) ->
  server_a!{get_floor, self()},
  receive
    {floor, Floor} -> respond(200, Floor)
  end;

do(#mod{request_uri="/position", method="GET"}) ->
  server_a!{get_pos, self()},
  receive
    {pos, Pos} -> respond(200, Pos)
  end;

do(#mod{request_uri="/saying", method="GET"}) ->
  server_a!{get_say, self()},
  receive
    {saying, Saying} -> respond(200, Saying) 
  end;

do(#mod{request_uri="/floor", method="POST", entity_body=Data}) ->
  server_a!{put_floor, Data},
  respond(200, "");

do(#mod{request_uri="/position", method="POST", entity_body=Data}) ->
  server_a!{put_pos, Data},
  respond(200, "");

do(Mod=#mod{request_uri="/saying", method="POST", entity_body=Data}) ->
  server_a!{put_say, Data},
  respond(200, "");

do(Mod=#mod{request_uri="/input", method="POST", entity_body=Data}) ->
  io:fwrite("Input data: ~p~n", [Data]),
  erlang:open_port({spawn_executable, "/usr/bin/python3"}, [{args, ["/home/pi/test1.py", Data]}, use_stdio, stderr_to_stdout]),
  respond(200, "");

do(Data) ->
  io:fwrite("Data: ~p~n", [Data]),
  respond(404, "").


