class Node():  # 定义Node类
    def __init__(self, data):
        self.data = data  # 数据域存储数据元素的值
        self.next = None  # 指针域存储下一个结点的地址


class SingleLinkedList:
    def __init__(self):
        self.head = Node(None)  # 创建Node对象，让头指针head指向头结点

    def CreateSingleLinkedList(self):  # 创建一个单链表
        cNode = self.head  # 将头结点作为当前结点
        Element = input("请输入当前结点的值：\n")  # 输入结点数据域的值
        nNode = Node(int(Element))  # 创建一个新结点
        nNode.next = cNode.next
        # 在以下横线处补充适当代码，使用Node类实现链表的建立。（注意：先删除横线，再填写代码）
        cNode.next = nNode  # 将新结点链入单链表的首部

    def PrintElement(self):
        cNode = self.head
        if cNode.next == None:
            print("当前单链表为空！")
            return
        print("当前单链表为：")
        while cNode.next != None:
            # 在以下横线处补充适当代码，移动到下一个结点。（注意：先删除横线，再填写代码）
            cNode = cNode.next  # 移动到下一个结点
            print(cNode.data, end="\t")
        print()


# 主程序
sList = SingleLinkedList()
n = int(input('输入要创建链表的元素个数：\n'))
for i in range(n):
    sList.CreateSingleLinkedList()
sList.PrintElement()  # 输出链接