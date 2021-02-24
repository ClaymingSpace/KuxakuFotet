from .policy_aux import get_output_amount


# DAI functions

def addLiquidity_DAI(params, substep, state_history, prev_state, p_input):
    """ Adds Liquidity to Token Pool

    Mechanism to add liquidity to a Token's Pool and 
    user receives liquidity tokens

    Args:
        params (dict): Py dict containing sys params
        substep (int): Int value representing a step within a single timestep
        state_history (list): Py list of all previous states
        prev_state (dict): Py dict that defines what the state of the system was at
                            previous timestep or substep
        policy_input (dict): Py dict of signals or actions from Policy Functions

    Returns:
        tuple: key as State Variable name, and value as any Python type
        example:
    """    
    eth_reserve_pool = int(s['ETH_balance'])
    dai_reserve_pool = int(s['DAI_balance'])
    if p_input['eth_deposit'] == 0:
        token_amount = 0
    else:
        token_amount = int(p_input['eth_deposit'] * dai_reserve_pool // eth_reserve_pool + 1)
    return ('DAI_balance', dai_reserve_pool + token_amount)


def removeLiquidity_DAI(_params, substep, sH, s, _input):
    token_reserve = int(s['DAI_balance'])
    pct_amount = _input['KFX_pct']
    amount = token_reserve * pct_amount
    return ('DAI_balance', int(token_reserve - amount))


def ethToToken_DAI(_params, substep, sH, s, _input):
    delta_I = int(_input['eth_sold']) #amount of ETH being sold by the user
    I_t = int(s['ETH_balance'])
    O_t = int(s['DAI_balance'])
    if delta_I == 0:
        return ('DAI_balance', O_t)
    else:
        delta_O = int(get_output_amount(delta_I, I_t, O_t, _params))
        return ('DAI_balance', O_t - delta_O)


def tokenToEth_DAI(_params, substep, sH, s, _input):
    delta_I = int(_input['tokens_sold']) #amount of tokens being sold by the user
    I_t = int(s['DAI_balance'])
    return ('DAI_balance', I_t + delta_I)


# ETH functions

def addLiquidity_ETH(_params, substep, sH, s, _input):
    eth_reserve = int(s['ETH_balance'])
    return ('ETH_balance', eth_reserve + _input['eth_deposit'])


def removeLiquidity_ETH(_params, substep, sH, s, _input):
    eth_reserve = int(s['ETH_balance'])
    pct_amount = _input['KFX_pct']
    amount = pct_amount * eth_reserve
    return ('ETH_balance', int(eth_reserve - amount))


def ethToToken_ETH(_params, substep, history, s, _input):
    delta_I = int(_input['eth_sold']) #amount of ETH being sold by the user
    I_t = int(s['ETH_balance'])
    return ('ETH_balance', I_t + delta_I)


def tokenToEth_ETH(_params, substep, sH, s, _input):
    delta_I = int(_input['tokens_sold']) #amount of tokens being sold by the user
    O_t = int(s['ETH_balance'])
    I_t = int(s['DAI_balance'])
    if delta_I == 0:
        return ('ETH_balance', O_t)
    else:
        delta_O = int(get_output_amount(delta_I, I_t, O_t, _params))
        return ('ETH_balance', O_t - delta_O)
    

# KFX functions

def addLiquidity_KFX(params, substep, state_history, prev_state, p_input):
    """ Adds Liquidity to Token Pool

    Mechanism to add liquidity to a Token's Pool and 
    user receives liquidity tokens

    Args:
        params (dict): Py dict containing sys params
        substep (int): Int value representing a step within a single timestep
        state_history (list): Py list of all previous states
        prev_state (dict): Py dict that defines what the state of the system was at
                            previous timestep or substep
        p_input (dict): Py dict of signals or actions from Policy Functions

    Returns:
        tuple: key as State Variable name, and value as any Python type
        example:
    """
    total_liquidity = int(prev_state['KFX_supply'])
    eth_reserve = int(prev_state['ETH_balance'])
    liqTokens_minted = int(p_input['eth_deposit'] * total_liquidity // eth_reserve)
    return ('KFX_supply', total_liquidity + liqTokens_minted)


def removeLiquidity_KFX(_params, substep, sH, s, _input):
    total_liquidity = int(s['KFX_supply'])
    pct_amount = _input['KFX_pct']
    amount = total_liquidity * pct_amount
    return ('KFX_supply', int(total_liquidity - amount))