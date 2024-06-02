export const Operation = Object.freeze({
    TUNNEL_CLOSED: -101,
    TUNNEL_CONNECTION: 101,

    CLUSTER_REGISTRATION_SUCCESSFUL: 201,
    CLUSTER_REGISTRATION_FAILURE: 301,

    CLUSTER_EVENT_FETCHING_SUCCESSFUL: 501,
    CLUSTER_EVENT_FETCHING_FAILURE: 601,

    CLUSTER_ATTACK_DISTRIBUTION_SUCCESSFUL: 801,
    CLUSTER_ATTACK_DISTRIBUTION_FAILURE: 901,

    CLUSTER_HEALTH_SUCCESSFUL: 1101,
    CLUSTER_HEALTH_FAILURE: 1201
});

export const Events = Object.freeze({
    TunnelConnection: 'tunnel_connection',
    TunnelDisconnection: 'tunnel_disconnection',

    AttackDistributionUpdate: 'attack_distribution_update',
    
    AccessLogUpdate: 'access_log_update',
    SecurityLogUpdate: 'security_log_update',

    WafHealthUpdate: 'waf_health_update',
    WafServicesUpdate: 'waf_services_update',
    WafWorking: 'waf_working'
});