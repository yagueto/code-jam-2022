export type wsResponse = {
    type: string,
    status: boolean,
    data: object,
    error: object
}

export type player = {
    nickname: string,
    ready: boolean
}
