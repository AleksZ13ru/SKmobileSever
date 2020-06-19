import graphene
import graphql_jwt
import asyncio
from datetime import datetime

import users.schema
import machines.schema


class Query(users.schema.Query, machines.schema.Query, graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(root, info):
        return 'Hello, world!'


class Subscription(graphene.ObjectType):
    time_of_day = graphene.Field(graphene.String)

    async def subscribe_time_of_day(root, info):
        while True:
            yield {'time_of_day': datetime.now().isoformat()}
            await asyncio.sleep(10)


class Mutation(users.schema.Mutation, machines.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)

# SCHEMA = graphene.Schema(query=Query, subscription=Subscription)

