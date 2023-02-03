from yoomoney import Client, Account
from yoomoney import Quickpay

#
quickpay = Quickpay(
            receiver="4100117795337162",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=100,
            label="102_50_1"
            )
print(quickpay.base_url)
print(quickpay.redirected_url)



#
# token = "4100117795337162.E8F6B73BDDEB28D8E2F22DE94637417470B89D4D4AF107764C270C00528196D9A2416F8477A64FED693253EA68DADA8CC5A69289F0AA90A9D1DF2500153C70D85181DE2F62D448BD533BB59FBE58EB7327EFC98896704245756A1BB41A5A8791B56ECCE7C717A14AC26D790802094CE86930C5A6CEC1717D617FEB60959F871C"
# client = Client(token)
#
# history = client.operation_history(label="a1b2c3d4e7")
# print(history)
# print("List of operations:")
# print("Next page starts with: ", history.next_record)
# print(history.operations[0].status)
# for operation in history.operations:
#     print()
#     print("Operation:",operation.operation_id)
#     print("\tStatus     -->", operation.status)
#     print("\tDatetime   -->", operation.datetime)
#     print("\tTitle      -->", operation.title)
#     print("\tPattern id -->", operation.pattern_id)
#     print("\tDirection  -->", operation.direction)
#     print("\tAmount     -->", operation.amount)
#     print("\tLabel      -->", operation.label)
#     print("\tType       -->", operation.type)