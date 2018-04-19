'''
每隔5天获取一次收益率排名前15的股票 并购买持有五天卖出
'''


def initialize(account):

    account.day = 0
    get_iwencai('每隔5天获取一次收益率排名前15')


def gp_del_no_trade(account, data):
    for j in range(len(account.iwencai_securities) - 1, -1, -1):
        if data.current(account.iwencai_securities[j])[account.iwencai_securities[j]].is_paused == 1:
            del account.iwencai_securities[j]
    return account.iwencai_securities


def handle_data(account, data):
    gp_del_no_trade(account, data)
    log.info('初始股票池 ：' + str(account.iwencai_securities))
    log.info('持有股票池 ：' + str(list(account.positions)))

    if len(list(account.positions)) != len(account.iwencai_securities):
        for i in account.iwencai_securities:
            #log.info('初始股票池new ：' + str(account.iwencai_securities))
            #log.info('持有股票池new ：' + str(list(account.positions)))
            # if i not in account.positions:
            order(i, 1000)
            log.info('买入' + i)

    if len(list(account.positions)) == len(account.iwencai_securities):
        account.day += 1
        log.info('持有天数为' + str(account.day))

    if account.day == 5:
        for j in list(account.positions):
            order(j, -1000)
            log.info('卖出' + j)
            account.day = 0
