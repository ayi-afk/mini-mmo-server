from server.server import register_handler
from server.message_type import MessageType
from server.message import Message

from server.proto.PlayerJoin_pb2 import (
    PlayersResponse, JoinRequest, PlayerJoin)
from server.service.player import PlayerService
from server.service.character import CharacterService


@register_handler(MessageType.join_request)
async def player_join(message, client, broadcast):
    info = JoinRequest()
    info.ParseFromString(message.serialized_message)

    with CharacterService() as service:
        character = service.get(info.character_id)

    with PlayerService() as service:
        players = service.get_all()
        characters = [player.character for player in players]
        character = service.session.merge(character)
        service.create(character)

    client.player_id = info.character_id

    players_response = PlayersResponse()

    for other_character in characters:
        player_info = players_response.players.add()
        player_info.player_id = other_character.id
        x, y = other_character.get_position()
        player_info.x = x
        player_info.y = y
        player_info.velocity_x = other_character.velocity_x
        player_info.velocity_y = other_character.velocity_y
        player_info.color = other_character.color
        player_info.name = other_character.name

    client.send(Message(
        message_type=MessageType.players_response,
        message=players_response))

    player_join = PlayerJoin()
    player_join.player_id = client.player_id
    x, y = character.get_position()
    player_join.x = x
    player_join.y = y
    player_join.color = character.color
    player_join.name = character.name

    await broadcast(Message(
        message_type=MessageType.player_join,
        message=player_join),
        exclude=client)


@register_handler(MessageType.players_request)
async def players_state(message, client, broadcast):
    if not client.player_id:
        raise Exception('Received players_request event for invalid player!')

    players_response = PlayersResponse()

    with PlayerService() as service:
        players = service.get_all()

    for player in players:
        if player.id == client.player_id:
            continue

        character = player.character

        player_info = players_response.players.add()
        player_info.player_id = player.id
        x, y = character.get_position()
        player_info.x = x
        player_info.y = y
        player_info.velocity_x = character.velocity_x
        player_info.velocity_y = character.velocity_y

    client.send(Message(
        message_type=MessageType.players_response,
        message=players_response))