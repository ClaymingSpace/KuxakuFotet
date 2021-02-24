from .policy_aux import *
from .suf_aux import *

# Policies

def p_actionDecoder(_params, substep, sH, s):
    """ The Policy Action Decoder inside the PSUB
    
    Args:
        params (dict): Py dict containing sys params
        substep (int): Int value representing a step within a single timestep
        sH (list): Py list of all previous states
        s (dict): Py dict that defines what the state of the system was at
                            previous timestep or substep

    Returns:
        action (dict): key as Signal name, and value as any Python type
    """
    uniswap_events = _params['uniswap_events']
    
    prev_timestep = s['timestep']
    if substep > 1:
        prev_timestep -= 1
        
    #skip the first two events, as they are already accounted for in the initial conditions of the system
    t = prev_timestep + 2 
    
    # Initiatize all actions in dict
    action = {
        'eth_sold': 0,
        'tokens_sold': 0,
        'eth_deposit': 0,
        'KFX_burn': 0, 
        'KFX_pct': 0,
        'fee': 0,
        'conv_tol': 0,
        'price_ratio': 0
    }

    # Event variables
    event = uniswap_events['event'][t]
    # Storing all events in the current/previous state (s) into action dict under key 'action_id'
    action['action_id'] = event

    if event in ['TokenPurchase', 'EthPurchase']:
        # Parsing Data from Ethereum Tx data (uniswap_events) under an 'action_key' that
        # equates to the 'action' dict keys above.
        I_t, O_t, I_t1, O_t1, delta_I, delta_O, action_key = get_parameters(uniswap_events, event, s, t)
        # Conditional to check sys_param is -1
        if _params['retail_precision'] == -1:
            action[action_key] = delta_I
        elif classifier(delta_I, delta_O, _params['retail_precision']) == "Conv":            #Convenience trader case
            calculated_delta_O = int(get_output_amount(delta_I, I_t, O_t, _params))
            if calculated_delta_O >= delta_O * (1-_params['retail_tolerance']):
                action[action_key] = delta_I
            else:
                action[action_key] = 0
            action['price_ratio'] =  delta_O / calculated_delta_O
        else:            #Arbitrary trader case
            P = I_t1 / O_t1
            actual_P = I_t / O_t
            if(actual_P > P):
                I_t, O_t, I_t1, O_t1, delta_I, delta_O, action_key = get_parameters(uniswap_events, reverse_event(event), s, t)
                P = I_t1 / O_t1
                actual_P = I_t / O_t
                delta_I = get_delta_I(P, I_t, O_t, _params)
                delta_O = get_output_amount(delta_I, I_t, O_t, _params)
                if(unprofitable_transaction(I_t, O_t, delta_I, delta_O, action_key, _params)):
                    delta_I = 0
                action[action_key] = delta_I
            else:
                delta_I = get_delta_I(P, I_t, O_t, _params)
                delta_O = get_output_amount(delta_I, I_t, O_t, _params)
                if(unprofitable_transaction(I_t, O_t, delta_I, delta_O, action_key, _params)):
                    delta_I = 0
                action[action_key] = delta_I
    elif event == 'AddLiquidity':
        delta_I = uniswap_events['eth_delta'][t]
        action['eth_deposit'] = delta_I
    elif event == 'Transfer':
        KFX_delta = uniswap_events['uni_delta'][t]
        KFX_supply = uniswap_events['UNI_supply'][t-1]
        if KFX_delta < 0:
            action['KFX_burn'] = -KFX_delta
            action['KFX_pct'] = -KFX_delta / KFX_supply
    del uniswap_events
    return action

def profitable(P, delta_I, delta_O, action_key, _params):
    gross_profit = (delta_O*P) - delta_I
    if(action_key == 'token'):
        convert_to_ETH = gross_profit/P
        is_profitable = (convert_to_ETH > _params['fix_cost'])
    else:
        is_profitable = (gross_profit > _params['fix_cost'])


# Mechanisms (or) State Update Functions (SUFs)

def s_mechanismHub_DAI(_params, substep, sH, s, _input):
    action = _input['action_id']
    if action == 'TokenPurchase':
        return ethToToken_DAI(_params, substep, sH, s, _input)
    elif action == 'EthPurchase':
        return tokenToEth_DAI(_params, substep, sH, s, _input)
    elif action == 'AddLiquidity':
        return addLiquidity_DAI(_params, substep, sH, s, _input)
    elif action == 'Transfer':
        return removeLiquidity_DAI(_params, substep, sH, s, _input)
    return('DAI_balance', s['DAI_balance'])
    
def s_mechanismHub_ETH(_params, substep, sH, s, _input):
    action = _input['action_id']
    if action == 'TokenPurchase':
        return ethToToken_ETH(_params, substep, sH, s, _input)
    elif action == 'EthPurchase':
        return tokenToEth_ETH(_params, substep, sH, s, _input)
    elif action == 'AddLiquidity':
        return addLiquidity_ETH(_params, substep, sH, s, _input)
    elif action == 'Transfer':
        return removeLiquidity_ETH(_params, substep, sH, s, _input)
    return('ETH_balance', s['ETH_balance'])

def s_mechanismHub_KFX(_params, substep, sH, s, _input):
    action = _input['action_id']
    if action == 'AddLiquidity':
        return addLiquidity_KFX(_params, substep, sH, s, _input)
    elif action == 'Transfer':
        return removeLiquidity_KFX(_params, substep, sH, s, _input)
    return('KFX_supply', s['KFX_supply'])

def s_price_ratio(_params, substep, sH, s, _input):
    return('price_ratio',_input['price_ratio'])