# 定义结点类Node
class Node:
    def __init__(self,d):
        self.data=d
        self.next=None

# 生成单链表并输出链表的结点
a="123"
head=Node(None)            #生成头结点
head.next=Node(10)         #生成首结点
p=Node(a)                  #生成新结点
# 在以下begin...end之间插入p结点到head与首结点之间
##########begin1##########
p.next=head.next
head.next=p

########## end1 ##########
#p=a=None            #清除p与a ？
# 在以下begin...end之间通过head输出链表2个结点的值。
##########begin2##########
print(head.next.data)
print(head.next.next.data)

########## end2 ##########