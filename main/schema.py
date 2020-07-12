import graphene
import graphql_jwt
from rx import Observable
import asyncio
from datetime import datetime

import users.schema
import machines.schema
import massmeters.schema


class Query(users.schema.Query, machines.schema.Query, massmeters.schema.Query, graphene.ObjectType):
    pass


class Subscription(graphene.ObjectType):
    time_of_day = graphene.Field(graphene.String)

    async def subscribe_time_of_day(root, info):
        while True:
            yield {'time_of_day': datetime.now().isoformat()}
            await asyncio.sleep(10)


# class Subscription(graphene.ObjectType):
#     hello = graphene.String()
#
#     def resolve_hello(root, info):
#         return Observable.interval(3000) \
#                          .map(lambda i: "hello world!")

# class Subscription(ObjectType):
#     time_of_day = Field(String)
#
#     async def subscribe_time_of_day(root, info):
#         while True:
#             yield { 'time_of_day': datetime.now().isoformat()}
#             await asyncio.sleep(1)


class Mutation(users.schema.Mutation, machines.schema.Mutation, massmeters.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
