export const Operation = Object.freeze({
    CLUSTER_REGISTRATION_SUCCESSFUL: 101,
    CLUSTER_REGISTRATION_FAILURE: 201,

    CLUSTER_EVENT_FETCHING_SUCCESSFUL: 501,
    CLUSTER_EVENT_FETCHING_FAILURE: 601
});

export const Events = Object.freeze({
    TunnelConnection: 'tunnel_connection',
    TunnelDisconnection: 'tunnel_disconnection',

    ClusterUpdate: 'cluster_update',
    
    AccessLogUpdate: 'access_log_update',
    SecurityLogUpdate: 'security_log_update'
});